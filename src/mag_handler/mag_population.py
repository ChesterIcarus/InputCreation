from collections import defaultdict
import csv
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, T

from mag_handler.encoded_data_util import MagConvIndex, coordinate


class MagAgent:
    p_num: int
    hh_num: int
    home_maz: int
    mag_pnum: int
    mag_hhid: int
    trip_count: int
    trips: List[Tuple[T, ...]]

    def __init__(self, p_num, hh_num, home_maz=0, mag_pnum=0, mag_hhid=0):
        self.p_num = p_num
        self.hh_num = hh_num
        self.home_maz = home_maz
        self.mag_pnum = mag_pnum
        self.mag_hhid = mag_hhid
        self.trip_count = 0
        self.trips = list()

    def add_trip(self, trip: List[T]):
        trip = list(trip)
        trip.append(self.trip_count)
        self.trips.append(tuple(trip))
        self.trip_count += 1

    def clean_trips(self, conv: MagConvIndex):
        keys = [
            conv.orig_end,
            conv.dest_start,
            conv.dest_dur,
            conv.leg_time
        ]
        for index, value in enumerate(self.trips):
            trip = list(value)
            for key in keys:
                if trip[key] < 0:
                    trip[key] = 0
            self.trips[index] = tuple(trip)

    def get_trips(self):
        if self.trip_count == 1:
            return self.trips[0]
        return self.trips


class MagHousehold:
    hh_num: int
    mag_hhid: int
    agents: Dict[int, MagAgent]
    maz: int
    apn: str
    coord: coordinate = None

    def __init__(self, hh_num, mag_hhid=0, maz=0, apn='0'):
        self.hh_num = hh_num
        self.mag_hhid = mag_hhid
        self.agents = dict()
        self.maz = maz
        self.apn = apn
        self.coord = None

    def agent(self, p_num, mag_pnum=0, mag_hhid=0) -> MagAgent:
        self.agents[p_num] = MagAgent(p_num, self.hh_num,
                                      mag_pnum=mag_pnum, mag_hhid=mag_hhid)
        return self.agents[p_num]

    def agent_exist(self, p_num, mag_pnum=0, mag_hhid=0) -> Tuple[MagAgent, bool]:
        ''' Bool flag is False if new agent created, true if agent exists'''
        if p_num in self.agents:
            return (self.agents[p_num], True)
        else:
            return (self.agent(p_num, mag_pnum=mag_pnum, mag_hhid=mag_hhid),
                    False)

    def create_maz(self, origin_index):
        agent_origin_list = set([agent.trips[0][origin_index]
                                 for agent in list(self.agents.values())])
        if len(agent_origin_list) <= 1:
            self.maz = agent_origin_list.pop()
        else:
            raise ValueError("""Invalid agents from same household.
                                Must have matching origin MAZ\'s""")


class MagPopulation:
    proportion: int
    households: Dict[int, MagHousehold]
    conv: MagConvIndex

    def __init__(self, conv: MagConvIndex, proportion=1.0):
        self.proportion = proportion
        self.households = dict()
        self.conv = conv

    def define_agents(self, plans: pd.DataFrame, count=False):
        # TODO: Investigate using dask for speedup on this as well
        hh_count = 0
        p_count = 0

        for row in plans.itertuples(index=False, name=None):
            pnum = row[self.conv.pnum]
            hhid = row[self.conv.hhid]
            if hhid in self.households:
                self.households[hhid].agent_exist(pnum, mag_pnum=pnum,
                                                  mag_hhid=hhid)
                self.households[hhid].agents[pnum].add_trip(row)
            else:
                self.households[hhid] = MagHousehold(hhid, mag_hhid=hhid)
                self.households[hhid].agents[pnum] = MagAgent(pnum, hhid,
                                                              mag_pnum=pnum, mag_hhid=hhid)

                self.households[hhid].agents[pnum].add_trip(row)

        # Need to remove the sub-zero MAG errors from trips
        # after we have defined every agent
        household: MagHousehold
        for household in list(self.households.values()):
            household.create_maz(self.conv.orig_loc)
            agent: MagAgent
            for agent in list(household.agents.values()):
                agent.clean_trips(self.conv)
                agent.home_maz = household.maz

        if count:
            return {'agent': p_count, 'household': hh_count}
