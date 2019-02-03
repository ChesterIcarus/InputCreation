import dill
from getpass import getpass
from typing import List, Dict, Tuple, T


from mag_handler.mag_population import MagAgent, MagHousehold, MagPopulation
from util.db_util import DatabaseHandle


class PopulationUtil:
    population: MagPopulation = None

    def __init__(self, population=None):
        self.population = population
        pass

    def create_db(self, db_handle, write_max=0):
        ''' For writing all plan '''
        row_list = list()
        for house in list(self.population.households.values()):
            for agent in list(house.agents.values()):
                row_list.extend(self.create_row(agent))

    def create_table(self):
        pass

    def create_row(self, agent: MagAgent) -> List[Tuple[T, ...]]:
        p_num = agent.p_num
        hh_num = agent.hh_num
        mag_pid = agent.mag_pid
        mag_hhid = agent.mag_hhid

        # p_num, hh_num, orig_maz, depart_min, orig_purp, mode, dest_maz, arrive_min, dest_purp, dest_time, travel_min

        for trip in agent.trips:
            tmp = list()
            print(trip)
            input()
        return []
