import dill
import json
from getpass import getpass
from mag_handler.mag_controller import MagController
from mag_handler.matsim_plan import MatsimAct, MatsimLeg
from mag_handler.matsim_xml_writer import MatsimXml
from mag_handler.population_util import PopulationUtil

with open('src/config/config.json', 'r') as handle:
    config = json.load(handle)

params = config['FULL']

with open(params['mapping_path'], 'r') as handle:
    apn_maz_mapping = json.load(handle)

pw = getpass()
params['database']['password'] = pw
pop_util = PopulationUtil(params['database'])

handler = MagController(params['mag_indexes'])
plans = handler.plans_by_col(params['mag_path'],
                             params['mag_column_ids'])
population = handler.plans_to_population(plans)

pop_util.population = population
pop_util.create_db()

# print(len(plans))
# print(plans[0:10])
# print(len(population.households[1].agents[1].trips))
# print(len(list(population.households.keys())))
# print(len(list(population.households[1].agents.keys())))
population.household_to_coord(apn_maz_mapping)
matsim = handler.population_to_matsim(population)

writer = MatsimXml(location_type='coord')
writer.write(matsim, params['xml_output_path'])
