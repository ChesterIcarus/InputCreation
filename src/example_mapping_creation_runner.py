import json
import pandas as pd
from more_itertools import take
import sqlalchemy
import pyodbc


from mag_handler.mapping_creation import MappingCreation

if __name__ == '__main__':
    with open('config/mag_to_matsim_config.json', 'r') as handle:
        config = json.load(handle)
        params = config['TEST']
    # zones = example.zone_counts(
    #     example.read_csv(params['mag_mapping']['source_path']))
    # with open('zones.json', 'w+') as handle:
    #     json.dump(zones, handle)

    # with open(params['mag_mapping']['source_path'], 'r') as raw:

    mapping_create = MappingCreation()
    mapping_data = mapping_create.process(pd.read_csv(
        params['mag_mapping']['source_path']))
    # set up connection to database(with username/pw if needed)
    # engine = sqlalchemy.create_engine(f"mysql+mysqldb://{base_database['user']}" +
    #                                   f":{base_database['password']}@" +
    #                                   f"{base_database['host']}/" +
    #                                   f"{base_database['db']}")
    # mapping_data.to_sql('apn_maz_mapping', engine)
