from collections import defaultdict
import csv
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, T
from functools import partial

from mag_handler.encoded_data_util import MagConvIndex, Coordinate


class MagAgent:
    p_num: int
    hh_num: int
    mag_pid: int
    mag_hhid: int
    trip_count: int
    trips: List[Tuple[T, ...]]

    def __init__(self, p_num, hh_num, mag_pid=0, mag_hhid=0):
        self.p_num = p_num
        self.hh_num = hh_num
        self.mag_pid = mag_pid
        self.mag_hhid = mag_hhid
        self.trip_count = 0
        self.trips = list()

    def add_trip(self, trip: List[T]):
        self.trips.append(tuple(trip))
        self.trip_count += 1

    def get_trips(self):
        if self.trip_count == 1:
            return self.trips[0]
        return self.trips


class MagHousehold:
    hh_num: int
    # NOTE: mag_hhid is never used and just there as a reference
    mag_hhid: int
    agents: Dict[int, MagAgent]
    apn: int = None
    coord: Coordinate = Coordinate()

    def __init__(self, hh_num, mag_hhid=0, apn=0):
        self.hh_num = hh_num
        self.mag_hhid = mag_hhid
        self.agents = dict()
        self.apn = apn
        self.coord = Coordinate()

    def agent(self, p_num) -> MagAgent:
        try:
            return self.agents[p_num]
        except KeyError:
            self.agents[p_num] = MagAgent(p_num, self.hh_num)
        return self.agents[p_num]

    def agent_exist(self, p_num, mag_pid=0, mag_hhid=0) -> Tuple[MagAgent, bool]:
        ''' Bool flag is False if new agent created, true if agent exists'''
        try:
            return (self.agents[p_num], True)
        except KeyError:
            self.agents[p_num] = MagAgent(
                p_num, self.hh_num, mag_pid=mag_pid, mag_hhid=mag_hhid)
        return (self.agents[p_num], False)


class MagPopulation:
    proportion: int
    households: Dict[int, MagHousehold]
    conv: MagConvIndex = None

    def __init__(self, conv: MagConvIndex, proportion=1.0):
        self.proportion = proportion
        self.households = dict()
        self.conv = conv

    def define_agents(self, plans: pd.DataFrame, count=False):
        hh_count = 0
        p_count = 0

        for row in plans.itertuples(index=False, name=None):
            # These reference the MAG id's themselves, not used currently
            pnum = row[self.conv.pnum]
            hhid = row[self.conv.hhid]
            if hh_count in self.households:
                if not self.households[hh_count].agent_exist(p_count, mag_pid=pnum, mag_hhid=hhid):
                    p_count += 1
                self.households[hh_count].agents[p_count].add_trip(row)
            else:
                self.households[hh_count] = MagHousehold(
                    hh_count, mag_hhid=hhid)
                self.households[hh_count].agents[p_count] = MagAgent(
                    p_count, hh_count, mag_pid=pnum, mag_hhid=hhid)
                self.households[hh_count].agents[p_count].add_trip(row)
                hh_count += 1
                p_count += 1

        if count:
            return {'agent': p_count, 'household': hh_count}

    def household_to_coord(self, apn_by_maz):
        for household in list(self.households.items()):
            agents = list(household[1].agents.values())
            maz = str(agents[0].trips[0][self.conv.orig_loc])
            # try:
            hh_apn_idx = np.random.randint(0, len(apn_by_maz[maz]))
            # except ValueError as val:
            #     print('size', len(apn_by_maz[maz]), 'maz', maz)
            hh_apn = apn_by_maz[maz][hh_apn_idx]
            self.households[household[0]].apn = hh_apn[0]
            self.households[household[0]].coord.x = hh_apn[1]
            self.households[household[0]].coord.y = hh_apn[2]

    def write_agent_apn_crosswalk(self, filename):
        with open(filename, 'w+') as handle:
            csv_writer = csv.writer(handle)
            for household in list(self.households.items()):
                for agent in list(household[1].agents.values()):
                    tmp = [agent.mag_pid, agent.mag_hhid,
                           household[1].apn, household[1].coord.x, household[1].coord.y]
                    csv_writer.writerow(tmp)
