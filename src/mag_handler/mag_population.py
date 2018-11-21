from collections import defaultdict
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, T
from functools import partial

from mag_leg import MagLeg
from encoded_data_util import MagConvIndex


class MagAgent:
    id_: int
    hhid: int
    pnum: int
    trips: int
    trip_list: List[Tuple[T, ...]]

    def __init__(self, id_, hhid=0, pnum=0):
        self.id_ = id_
        self.hhid = hhid
        self.pnum = pnum
        self.trips = 0
        self.trip_list = list()

    def add_trip(self, trip: List[T]):
        self.trip_list.append(tuple(trip))
        self.trips += 1

    def get_trips(self):
        if self.trips == 1:
            return self.trip_list[0]
        return self.trip_list


class MagHousehold:
    id_: int
    hhid: int
    agents: Dict[int, MagAgent]

    def __init__(self, id_, hhid=0):
        self.id_ = id_
        self.hhid = hhid
        self.agents = dict()

    def agent(self, id_) -> MagAgent:
        try:
            return self.agents[id_]
        except KeyError:
            self.agents[id_] = MagAgent(id_)
        return self.agents[id_]

    def agent_bool(self, id_) -> Tuple[MagAgent, bool]:
        ''' Bool flag is True if new agent created, false if agent exists'''
        try:
            return (self.agents[id_], False)
        except KeyError:
            self.agents[id_] = MagAgent(id_)
        return (self.agents[id_], True)


class MagPopulation:
    proportion: int
    households: Dict[int, MagHousehold]

    def __init__(self, proportion=1.0):
        self.proportion = proportion
        self.households = dict()

    def define_agents(self, plans: pd.DataFrame, conv: MagConvIndex, count=False):
        household_count = 0
        agent_count = 0

        for row in plans.itertuples(index=False, name=None):
            pnum = row[conv.pnum]
            hhid = row[conv.hhid]
            if hhid in self.households:
                if pnum in self.households[hhid].agents:
                    self.households[hhid].agents[pnum].add_trip(row)
                else:
                    self.households[hhid].agents[pnum] = MagAgent(agent_count)
                    self.households[hhid].agents[pnum].add_trip(row)
                    agent_count += 1
            else:
                self.households[hhid] = MagHousehold(household_count, hhid)
                self.households[hhid].agents[pnum] = MagAgent(agent_count)
                self.households[hhid].agents[pnum].add_trip(row)
                household_count
                agent_count += 1

        if count:
            return {'agent': agent_count, 'household': household_count}

    def convert_maz(self, coords_by_maz: Dict[List[Tuple[float, float]]]):
        pass
