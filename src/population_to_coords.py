import dill
import json
from getpass import getpass
from fsplit.filesplit import FileSplit
import os
from mag_handler.mag_controller import MagController
from mag_handler.matsim_plan import MatsimAct, MatsimLeg
from mag_handler.matsim_xml_writer import MatsimXml
from mag_handler.population_util import PopulationUtil
from mag_handler.mag_population import MagPopulation, MagHousehold, MagAgent
from mag_handler.encoded_data_util import MagConvIndex

with open('config/config.json', 'r') as handle:
    config = json.load(handle)
params = config['FULL']
# pw = getpass()
# params['database']['password'] = pw
# pop_util = PopulationUtil(params['database'])

handler = MagController(params['mag_indexes'])
with open(params['mapping_path'], 'r') as handle:
    apn_maz_mapping = json.load(handle)

sliced = False

if sliced:
    st = os.stat(params['mag_path'])
    split_size = 300000000
    mag_dir = '/'.join(params['mag_path'].split('/')[0:-1])

    fs = FileSplit(params['mag_path'], split_size, output_dir=mag_dir)
    fs.split(include_header=True)

    for i in range(1, (st.st_size % split_size) + 1):
        params['mag_path'] = f"../../data/raw_travel_data/output_disaggTripList_{i}.csv"

        plans = handler.plans_by_col(params['mag_path'],
                                     params['mag_column_ids'])
        population = handler.plans_to_population(plans)

        # with open(f'../../data/processed_MAG_data/population_{i}.dill', 'wb+') as handle:
        #     dill.dump(population, handle)

        # with open('../../data/processed_MAG_data/population.dill', 'rb') as handle:
        #     population: MagPopulation = dill.load(handle)

        print(f"{i} done")

        population.household_to_coord(apn_maz_mapping)
        population.write_agent_home_apn(
            f'agent_crosswalk_apn_maz_{i}.csv')
        del population
else:

    params['mag_path'] = "../../data/raw_travel_data/output_disaggTripList.csv"

    plans = handler.plans_by_col(params['mag_path'],
                                 params['mag_column_ids'])
    population = handler.plans_to_population(plans)

    # with open(f'../../data/processed_MAG_data/population_{i}.dill', 'wb+') as handle:
    #     dill.dump(population, handle)

    # with open('../../data/processed_MAG_data/population.dill', 'rb') as handle:
    #     population: MagPopulation = dill.load(handle)

    # print(f"{i} done")

    population.household_to_coord(apn_maz_mapping)
    population.write_agent_home_apn('agent_crosswalk_apn_maz.csv')
