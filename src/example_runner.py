import dill
import json
import pandas as pd
from getpass import getpass
import sqlalchemy


from mag_handler.mapping_creation import MappingCreation
from mag_handler.population_util import PopulationUtil
from mag_handler.encoded_data_util import MagConvIndex
from mag_handler.mag_controller import MagController
# from mag_handler.matsim_plan import MatsimAct, MatsimLeg
from mag_handler.mag_to_matsim import MagToMatsim
from mag_handler.matsim_xml_writer import MatsimXml
# from util.db_util import DatabaseHandle
from util.mapping_db_util import MappingDatabase

if __name__ == '__main__':
    config_path = 'InputCreation/src/config/mag_to_matsim_config.json'
    with open(config_path, 'r') as handle:
        config = json.load(handle)
        params = config['AWS']

    # We should be writing all the table to the same database
    # params['base_database']['password'] = getpass(
    #     f'Password for {params["base_database"]["user"]}: ')
    for db in [params['mag_population']['database'],
               params['mag_mapping']['database']]:
        for key, value in list(params['base_database'].items()):
            db[key] = value

    POPULATION_CONVERSION = True
    RUN_MAG_MAT = True

    mapping_param = params['mag_mapping']
    mag_param = params['mag_population']
    matsim_param = params['MATsim_plans']

    mag_db = mag_param['database']
    pop_util = PopulationUtil(mag_db)

    mapping_create = MappingCreation()
    mapping_no_rand_id = mapping_create.read_csv(
        mapping_param['source_path'])
    mapping_data = mapping_create.process(mapping_no_rand_id)
    # set up connection to database(with username/pw if needed)
    engine = sqlalchemy.create_engine(
        f"mysql+mysqldb://{mapping_param['database']['user']}" +
        f":{mapping_param['database']['password']}@" +
        f"{mapping_param['database']['host']}/" +
        f"{mapping_param['database']['db']}")
    mapping_data.to_sql(mapping_param['database']['table'], engine)

    # Connection to the mapping db, as well as the # of APN per MAZ
    mapping_database = MappingDatabase(mapping_param['database'])
    mapping_database.load_zone_counts(params['mag_mapping']['zone_counts'])

    index_conversion = MagConvIndex(mag_param['indexes'])

    if RUN_MAG_MAT:
        if POPULATION_CONVERSION:
            controller = MagController(index_conversion)

            # Filepath for MAG data
            # Column ID's to retain from the dataset
            plans = controller.plans_by_col(mag_param['source_path'],
                                            mag_param['column_ids'])
            # Turn the CSV plans into an encoded population
            # Allows for more specific recall of agents
            population = controller.plans_to_population(plans)

            # Create a table with the population given in the contructor
            pop_util.create_table(population=population,
                                  table=mag_db['table'],
                                  schema=mag_db['schema'],
                                  composite_key=mag_db['composite_key'])

            with open(mag_param['pickle_path'], 'wb+') as handle:
                dill.dump(population, handle)
                print(f'''Successfully wrote population to:
                            {mag_param["pickle_path"]}''')

        elif not POPULATION_CONVERSION:
            with open(mag_param['pickle_path'], 'rb') as handle:
                population = dill.load(handle)
                print(f'''Successfully loaded population from:
                            {mag_param["pickle_path"]}''')

        mag_to_mat = MagToMatsim(conv=index_conversion)
        matsim = mag_to_mat.convert(population, mapping_database)

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
    writer.write(matsim, matsim_param['xml_path'], use_mag=False)
