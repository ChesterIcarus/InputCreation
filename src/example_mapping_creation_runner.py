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
    example = MappingCreation()
    # zones = example.zone_counts(
    #     example.read_csv(params['mag_mapping']['source_path']))
    # with open('zones.json', 'w+') as handle:
    #     json.dump(zones, handle)

    # with open(params['mag_mapping']['source_path'], 'r') as raw:
    raw = pd.read_csv(params['mag_mapping']['source_path'])
    data = example.process(raw)
    data.to_csv('mapping_creation_TEST.csv')

    # set up connection to database(with username/pw if needed)
    # engine = sqlalchemy.create_engine(
    #     'mysql+mysqldb://root:Tory199&@localhost/icarus_TEST')
    # data.to_sql('apn_maz_mapping', engine)
