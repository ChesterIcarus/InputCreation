import dill
import json
import pandas as pd
from getpass import getpass
import sqlalchemy


from mag_handler.mapping_creation import MappingCreation
from mag_handler.population_util import PopulationUtil
from mag_handler.encoded_data_util import MagConvIndex
from mag_handler.mag_controller import MagController
from mag_handler.mag_to_matsim import MagToMatsim
from mag_handler.matsim_xml_writer import MatsimXml
from mag_handler.fast.fast_map import FastMap
from mag_handler.fast.matsim_plan import FastMatsimPlan, config


if __name__ == '__main__':
    config_path = 'InputCreation/src/config/aws_config.json'
    with open(config_path, 'r') as handle:
        config_json = json.load(handle)
        params = config_json['full']

    # We should be writing all the table to the same database
    RUN_MAG_MAT = False

    mapping_param = params['mag_mapping']
    mag_param = params['mag_population']
    matsim_param = params['MATsim_plans']

    fast_map = FastMap(mapping_param['fast_map_source'], None)
    config(fast_map)

    MagConvIndex(mag_param['indexes'])

    if RUN_MAG_MAT:
        controller = MagController()
        # Filepath for MAG data
        # Column ID's to retain from the dataset
        plans = controller.plans_by_col(mag_param['source_path'],
                                        mag_param['column_ids'])

        mag_to_mat = MagToMatsim(database=None,
                                 map_dict=None)
        # matsim = mag_to_mat.from_df(plans, fast_map)
        matsim = mag_to_mat.from_df_mp(plans)

        with open(matsim_param['pickle_path'], 'wb+') as handle:
            dill.dump(matsim, handle)
            print(f'''Successfully wrote MATsim Plans to:
                        {matsim_param["pickle_path"]}''')

    elif not RUN_MAG_MAT:
        with open(matsim_param['pickle_path'], 'rb') as handle:
            matsim = dill.load(handle)
            print(f'Successfully loaded MATsim Plans from' +
                  '{matsim_param["pickle_path"]}')

    writer = MatsimXml(location_type='coord')
    writer.write(matsim, matsim_param['xml_path'], use_mag=True)
