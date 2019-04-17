from typing import Dict, List, Tuple, T
from collections import namedtuple
from random import choice, shuffle
import numpy as np
import pandas as pd

from mag_handler.encoded_data_util import MagConvIndex
from mag_handler.mag_population import MagAgent
from mag_handler.encoded_data_util import coordinate, mode_encode, purpose_encode
from util.db_util import DatabaseHandle
from util.mapping_db_util import MappingDatabase
from mag_handler.fast.fast_map import FastMap


MatsimAct = namedtuple('MatsimAct', ['end_time',
                                     'duration',
                                     'apn',
                                     'maz',
                                     'coord',
                                     'purpose'])

MatsimLeg = namedtuple('MatsimLeg', ['mode',
                                     'dep_time',
                                     'trav_time'])

def config(fast_map: FastMap):
    map_sel = {k: [0, len(fast_map.data[k])-1] for k in fast_map.data}
    FastMatsimPlan.mapping_count = map_sel
    for key in fast_map.data:
        value = list(fast_map.data[key])
        shuffle(value)
        FastMatsimPlan.mapping[key] = value


class FastMatsimPlan:
    ''' Class creating a MATsim Plan, from a DataFrame
        Agent must have all properties, and mapping must include agents MAZ.
        Mapping must be a 4-column Df with: [maz, apn, x, y] '''
    person_id: int
    mag_pnum: int
    mag_hhid: int
    home_maz: int
    home_apn: str
    home_coord: coordinate
    mapping: Dict[int, List] = dict()
    mapping_count: Dict[int, List[List]]
    events: Tuple[T, ...]

    def __init__(self, trips: pd.DataFrame):
        self.trips = trips
        self.pnum = self.trips.iat[0, MagConvIndex.pnum]
        self.hhid = self.trips.iat[0, MagConvIndex.hhid]
        self.home_maz = self.trips.iat[0, MagConvIndex.orig_loc]
        home = self.random_apn(self.home_maz)
        self.home_apn = home[0]
        self.home_coord = coordinate(x=home[1], y=home[2])
        self.events = tuple([])
        self.create_plan()

    def random_apn(self, maz: int) -> T:
        ''' Random APN without using a database for it'''
        map_sel = FastMatsimPlan.mapping_count[maz]
        apn = FastMatsimPlan.mapping[maz][map_sel[0]]
        if map_sel[0] < map_sel[1]:
            map_sel[0] += 1
        else:
            map_sel[0] = 0
        return apn

    def single(self):
        ''' Create the MATsim plan for a trip with a single act'''
        initial_act = self.initial_act_creation()
        # Currently not using duration because MATsim doesn't require it
        # duration = trip[self.conv.leg_time]
        final_act = self.final_events_creation()
        self.events = (initial_act, *final_act)

    def multiple(self):
        initial_act = self.initial_act_creation()

        middle_events = list()
        for trip in range(self.trips.shape[0] - 1):
            middle_events.extend(self.standard_event_creation(trip))

        final_events = self.final_events_creation()
        self.events = (initial_act, *middle_events, *final_events)

    def initial_act_creation(self) -> MatsimAct:
        ''' If a MatsimAct is the first Act in a Plan,
            it has an end time but no duration. Purpose = Home. '''
        initial_trip = self.trips.iloc[0]
        if purpose_encode[initial_trip.iat[MagConvIndex.orig_type]] is 'home':
            orig_coord = self.home_coord
            orig_apn = self.home_apn
            orig_maz = self.home_maz
        else:
            orig_maz = initial_trip.iat[MagConvIndex.orig_loc]
            rand_apn = self.random_apn(orig_maz)
            orig_apn = rand_apn[0]
            orig_coord = coordinate(rand_apn[1], rand_apn[2])
        initial_act = MatsimAct(end_time=initial_trip.iat[MagConvIndex.orig_end],
                                duration=False,
                                purpose='home',
                                coord=orig_coord,
                                apn=orig_apn,
                                maz=orig_maz)
        return initial_act

    def final_events_creation(self) -> Tuple[MatsimLeg, MatsimAct]:
        ''' If a MatsimAct is the last Act in a Plan,
            it has no end time and no duration. Purpose = Home. '''
        final_trip = self.trips.iloc[-1]
        leg = MatsimLeg(mode_encode[final_trip.iat[MagConvIndex.mode]],
                                   final_trip.iat[MagConvIndex.orig_end],
                                   final_trip.iat[MagConvIndex.leg_time])
        dest_maz = final_trip.iat[MagConvIndex.dest_loc]
        dest = self.random_apn(dest_maz)
        act = MatsimAct(end_time=final_trip.iat[MagConvIndex.dest_dur]+\
                                   final_trip.iat[MagConvIndex.dest_start],
                                   duration=final_trip.iat[MagConvIndex.dest_dur],
                                   purpose=purpose_encode[
                                       final_trip.iat[MagConvIndex.dest_type]],
                                   coord=coordinate(dest[1],
                                                    dest[2]),
                                   apn=dest[0],
                                   maz=dest_maz)
        return (leg, act)

    def standard_event_creation(self, trip_num: int):
        ''' Give actor APNs and coordinate for trips based off MAZ/trip type
            trip_num: Index of trip to access from trips (DataFrame)'''
        trip = self.trips.iloc[trip_num]
        leg = MatsimLeg(mode_encode[trip.iat[MagConvIndex.mode]],
                        trip.iat[MagConvIndex.orig_end],
                        trip.iat[MagConvIndex.leg_time])
        dest_maz = trip.iat[MagConvIndex.dest_loc]
        dest = self.random_apn(dest_maz)
        act = MatsimAct(end_time=trip.iat[MagConvIndex.dest_start]+\
                        trip.iat[MagConvIndex.dest_dur],
                        duration=trip.iat[MagConvIndex.dest_dur],
                        purpose=purpose_encode[trip.iat[MagConvIndex.dest_type]],
                        coord=coordinate(dest[1],
                                         dest[2]),
                        apn=dest[0],
                        maz=dest_maz)
        return (leg, act)

    def create_plan(self):
        ''' A MAG travel diary n trips long yeilds:
                (n+1) MATsim Acts, and (n) MATsim Legs '''
        trip_count = self.trips.shape[0]
        if trip_count == 1:
            self.single()
        elif trip_count > 1:
            self.multiple()
        else:
            raise ValueError('Agents must have at least one valid Trip')
