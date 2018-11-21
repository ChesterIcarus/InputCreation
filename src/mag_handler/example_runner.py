# from configparser import ConfigParser
import json
from mag_handler import MagHandler
from matsim_plan import MatsimAct, MatsimLeg
from matsim_xml_writer import MatsimXml

# config = ConfigParser()
# config.read('config.json')
with open('config.json', 'r') as handle:
    config = json.load(handle)


handler = MagHandler(config['DEFAULT']['mag_indexes'])
plans = handler.plans_by_col(config['DEFAULT']['mag_data_filename'],
                             config['DEFAULT']['mag_columns_to_parse'])
pop = handler.plans_to_population(plans)

print(len(plans))
print(plans[0:10])

print(len(pop.households[1].agents[1].trip_list))
print(len(list(pop.households.keys())))
print(len(list(pop.households[1].agents.keys())))


matsim = handler.population_to_matsim(pop)
print(len(matsim))

writer = MatsimXml(location_type='maz')
writer.write(matsim, 'example_out.xml')
