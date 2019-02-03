import dill
from getpass import getpass
from typing import List, Dict, Tuple, T


from mag_handler.mag_population import MagAgent, MagHousehold, MagPopulation
from util.db_util import DatabaseHandle


class PopulationUtil:
    population: MagPopulation = None
    db = None

    def __init__(self, db_params, population=None):
        self.population = population
        self.db = DatabaseHandle(**db_params)

    def create_db(self, table_name='ModMag', custom_schema=False, write_max=0):
        ''' For writing all plan '''
        self.create_table(table_name, custom_schema=custom_schema)
        row_list = list()
        if write_max != 0:
            count = 0
            for house in list(self.population.households.values()):
                for agent in list(house.agents.values()):
                    rows = self.agent_to_rows(agent)
                    count += len(rows)
                    row_list.extend(rows)

                if count > write_max:
                    self.db.write_rows(row_list)
                    row_list.clear()
                    count = 0
            if len(row_list) != 0:
                self.db.write_rows(row_list)
        else:
            for house in list(self.population.households.values()):
                for agent in list(house.agents.values()):
                    row_list.extend(self.agent_to_rows(agent))
            self.db.write_rows(row_list)

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

    def agent_to_rows(self, agent: MagAgent) -> List[Tuple[T, ...]]:
        rows = list()
        for trip in agent.trips:
            trip = list(trip)
            for index in [12, 11, 10, 8]:
                if trip[index] < 0:
                    trip[index] = 0
            rows.append(tuple(trip))
        return rows
