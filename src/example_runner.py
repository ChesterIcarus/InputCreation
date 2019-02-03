# from configparser import ConfigParser
import dill
import json
from mag_handler.mag_controller import MagController
from mag_handler.matsim_plan import MatsimAct, MatsimLeg
from mag_handler.matsim_xml_writer import MatsimXml

# config = ConfigParser()
# config.read('config.json')
with open('config/config.json', 'r') as handle:
    config = json.load(handle)


handler = MagController(config['DEFAULT']['mag_indexes'])
plans = handler.plans_by_col(config['DEFAULT']['mag_data_filename'],
                             config['DEFAULT']['mag_columns_to_parse'])
pop = handler.plans_to_population(plans)

with open('../data/interim/full_population.dill', 'wb+') as handle:
    dill.dump(pop, handle)

exit(0)

print(len(plans))
print(plans[0:10])

print(len(pop.households[1].agents[1].trips))
print(len(list(pop.households.keys())))
print(len(list(pop.households[1].agents.keys())))


matsim = handler.population_to_matsim(pop)
print(len(matsim))

writer = MatsimXml(location_type='maz')
writer.write(matsim, 'example_out.xml')
