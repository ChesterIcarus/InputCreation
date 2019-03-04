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
    params = config['FULL']

    apn_maz_mapping = pd.read_csv(params['mapping_path'])

    # pw = getpass()
    # params['database']['password'] = pw
    # pop_util = PopulationUtil(params['database'])
    # pop_util.population = population
    index_conversion = MagConvIndex(params['mag_indexes'])

    controller = MagController(index_conversion)
    plans = controller.plans_by_col(params['mag_path'],
                                    params['mag_column_ids'])
    population = controller.plans_to_population(plans)

    with open('src/cleaned_mag_pop.pickle', 'wb+') as handle:
        dill.dump(population, handle)

    mag_to_mat = MagToMatsim(conv=index_conversion)
    matsim = mag_to_mat.convert(population, apn_maz_mapping)

    with open('src/matsim_plans.pickle', 'wb+') as handle:
        dill.dump(matsim, handle)

    writer = MatsimXml(location_type='coord')
    writer.write(matsim, params['xml_output_path'])
