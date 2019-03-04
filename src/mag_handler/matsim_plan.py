from typing import Dict, List, Tuple, T

import pandas as pd
from mag_handler.encoded_data_util import MagConvIndex
from mag_handler.mag_population import MagAgent
from mag_handler.encoded_data_util import Coordinate, Mode, Purpose


class MatsimAct:
    ''' Simple representation of MATsim Act '''
    end_time: T
    duration: T
    apn: str
    maz: int
    coord: Coordinate
    purpose: Purpose

    def __init__(self, end_time, duration, purpose: Purpose, coord: Coordinate, apn, maz):
        self.end_time = end_time
        self.duration = duration
        self.purpose = purpose
        self.coord = coord
        self.maz = maz
        self.apn = apn


class MatsimLeg:
    ''' Simple representation of MATsim Leg '''
    mode: Mode
    duration: str

    def __init__(self, mode: Mode, duration: str = ''):
        self.mode = mode
        self.duration = duration


class MatsimPlan:
    ''' Class creating a MATsim Plan, from a MAG agent.
        Agent must have all properties, and mapping must include agents MAZ.
        Mapping must be a 4-column Df with: [maz, apn, x, y] '''
    person_id: int
    mag_pnum: int
    mag_hhid: int
    home_maz: int
    home_apn: str
    home_coord: Coordinate
    conv: MagConvIndex

    events: List

    def __init__(self, agent: MagAgent, mapping: pd.DataFrame):
        self.mapping = mapping
        self.person_id = agent.p_num
        self.mag_pnum = agent.mag_pnum
        self.mag_hhid = agent.mag_hhid
        home = self.random_apn(agent.home_maz)
        self.home_maz = home[0]
        self.home_apn = home[1]
        self.home_coord = Coordinate(x=home[2], y=home[3])

    def random_apn(self, maz: int) -> str:
        ''' Get a random APN for a given MAZ. '''
        return self.mapping.loc[self.mapping['maz'] == maz].sample()

    def single(self, trip: Tuple[T, ...]):
        ''' '''
        initial_act = self.initial_act_creation(trip)

        # Currently not using duration because MATsim doesn't require it
        # duration = trip[self.conv.leg_time]
        leg = MatsimLeg(Mode(trip[self.conv.mode]))

        final_act = self.final_events_creation(trip)
        self.events = tuple([initial_act, leg, final_act])

    def multiple(self, trips: List[Tuple[T, ...]]):
        initial_act = self.initial_act_creation(trips[0])

        middle_events = list()
        for trip in trips[0:-1]:
            middle_events.extend(self.standard_event_creation(trip))

        final_events = self.final_events_creation(trip)
        self.events = tuple([initial_act, *middle_events, *final_events])

    def initial_act_creation(self, trip) -> MatsimAct:
        ''' If a MatsimAct is the first Act in a Plan,
            it has an end time but no duration. Purpose = Home. '''
        initial_act = MatsimAct(end_time=trip[self.conv.orig_end],
                                duration=False,
                                purpose=Purpose(0),
                                coord=self.home_coord,
                                apn=self.home_apn,
                                maz=self.home_maz)
        return initial_act

    def final_events_creation(self, trip) -> Tuple[MatsimLeg, MatsimAct]:
        ''' If a MatsimAct is the last Act in a Plan,
            it has no end time and no duration. Purpose = Home. '''
        final_leg = MatsimLeg(Mode(trip[self.conv.mode]))
        final_act = MatsimAct(end_time=False,
                              duration=False,
                              purpose=Purpose(0),
                              coord=self.home_coord,
                              apn=self.home_apn,
                              maz=self.home_maz)
        return tuple([final_leg, final_act])

    def standard_event_creation(self, trip):
        # Give actor APN's and coordinate for trips based off MAZ/trip type
        leg = MatsimLeg(Mode(trip[self.conv.mode]))
        dest = self.random_apn(trip[self.conv.dest_loc])
        act = MatsimAct(end_time=trip[self.conv.orig_end],
                        duration=False,
                        purpose=Purpose(trip[self.conv.orig_type]),
                        coord=Coordinate(dest[2], dest[3]),
                        apn=dest[1],
                        maz=dest[0])
        return [leg, act]

    def create_plan(self, agent: MagAgent):
        ''' A MAG travel diary n trips long yeilds: 
                (n+1) MATsim Acts, and (n) MATsim Legs '''
        self.plan = None
        if agent.trip_count == 1:
            self.single(agent.get_trips())
        elif agent.trip_count > 1:
            self.multiple(agent.get_trips())
        else:
            raise ValueError('Agents must have at least one valid Trip')
        self.events = tuple(self.events)
