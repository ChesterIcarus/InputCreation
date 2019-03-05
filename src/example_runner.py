import dill
import json
import pandas as pd
from getpass import getpass


from mag_handler.population_util import PopulationUtil
from mag_handler.encoded_data_util import MagConvIndex
from mag_handler.mag_controller import MagController
from mag_handler.matsim_plan import MatsimAct, MatsimLeg
from mag_handler.mag_to_matsim import MagToMatsim
from mag_handler.matsim_xml_writer import MatsimXml

if __name__ == '__main__':

    with open('config/config.json', 'r') as handle:
        config = json.load(handle)
        params = config['TEST']
    POPULATION_CONVERSION = False
    RUN_MAG_MAT = True

    apn_maz_mapping = pd.read_csv(params['mapping_path'])
    index_conversion = MagConvIndex(params['mag_indexes'])

    # pw = getpass()
    # params['database']['password'] = pw
    # pop_util = PopulationUtil(params['database'])
    # pop_util.population = population

    if RUN_MAG_MAT:
        if POPULATION_CONVERSION:
            controller = MagController(index_conversion)
            plans = controller.plans_by_col(params['mag_path'],
                                            params['mag_column_ids'])
            population = controller.plans_to_population(plans)
            with open(params['population_pickle_path'], 'wb+') as handle:
                dill.dump(population, handle)
                print('Successfully wrote population to: ' +
                      params['population_pickle_path'])
        else:
            with open(params['population_pickle_path'], 'rb') as handle:
                population = dill.load(handle)
                print('Successfully loaded population from: ' +
                      params['population_pickle_path'])

        mag_to_mat = MagToMatsim(conv=index_conversion)
        matsim = mag_to_mat.convert(population, apn_maz_mapping)
        with open(params['matsim_pickle_path'], 'wb+') as handle:
            dill.dump(matsim, handle)
            print('Successfully wrote MATsim Plans to: ' +
                  params['matsim_pickle_path'])

    else:
        with open(params['matsim_pickle_path'], 'rb') as handle:
            matsim = dill.load(handle)
            print('Successfully loaded MATsim Plans from: ' +
                  params['matsim_pickle_path'])

    writer = MatsimXml(location_type='coord')
    writer.write(matsim, params['xml_output_path'])
