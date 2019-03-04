import dill
from getpass import getpass
from typing import List, Dict, Tuple, T


from mag_handler.mag_population import MagAgent, MagHousehold, MagPopulation
from util.db_util import DatabaseHandle


class PopulationUtil:
    population: MagPopulation = None
    db: DatabaseHandle

    def __init__(self, db_params, population=None):
        self.population = population
        self.db = DatabaseHandle(**db_params)

    def create_db(self, table_name='ModMag', custom_schema=False, write_max=0):
        ''' For writing all plan '''
        self.create_table(table_name, custom_schema=custom_schema)
        trips = list()
        if write_max != 0:
            count = 0
            house: MagHousehold
            for house in list(self.population.households.values()):
                agent: MagAgent
                for agent in list(house.agents.values()):
                    count += agent.trip_count
                    trips.extend(agent.trips)

                if count > write_max:
                    self.db.write_rows(trips)
                    trips.clear()
                    count = 0
            if len(trips) != 0:
                self.db.write_rows(trips)
        else:
            house: MagHousehold
            for house in list(self.population.households.values()):
                agent: MagAgent
                for agent in list(house.agents.values()):
                    trips.extend(agent.trips)
            self.db.write_rows(trips)

    def create_table(self, table_name, custom_schema=False):
        schema = '''(
                        hh_num INT UNSIGNED, 
                        p_num INT UNSIGNED,
                        orig_maz INT UNSIGNED,
                        dest_maz INT UNSIGNED,
                        orig_purp INT UNSIGNED,
                        dest_purp INT UNSIGNED,
                        mode INT UNSIGNED,
                        depart_min DOUBLE,
                        trip_dist DOUBLE,
                        travel_min DOUBLE,
                        arrival_min DOUBLE,
                        time_at_dest DOUBLE,
                        pnr_park_maz INT UNSIGNED
                    )'''
        if custom_schema:
            schema = custom_schema
        self.db.create_db(table_name, schema)
