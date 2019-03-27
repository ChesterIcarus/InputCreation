import dill
from getpass import getpass
from typing import List, Dict, Tuple, T


from mag_handler.mag_population import MagAgent, MagHousehold, MagPopulation
from util.db_util import DatabaseHandle


class PopulationUtil:
    population: MagPopulation = None
    db: DatabaseHandle

    def __init__(self, db_params, population=None):
        self.db = DatabaseHandle(db_params)
        self.population = population

    def create_table(self, table, schema, composite_key, population=None, write_max=0):
        if population is not None:
            self.population = population
        ''' For writing all plan '''
        self.db.create_table(table, schema)
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

        self.db.alter_add_composite_key(pk_fields)
