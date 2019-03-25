from typing import Dict, List, Tuple, T
from collections import namedtuple

import pandas as pd
from mag_handler.encoded_data_util import MagConvIndex
from mag_handler.mag_population import MagAgent
from mag_handler.encoded_data_util import coordinate, mode_encode, purpose_encode


MatsimAct = namedtuple('MatsimAct', ['end_time',
                                     'duration',
                                     'apn',
                                     'maz',
                                     'coord',
                                     'purpose'])
MatsimLeg = namedtuple('MatsimLeg', 'mode')

# class MatsimAct:
#     ''' Simple representation of MATsim Act '''
#     end_time: T
#     duration: T
#     apn: str
#     maz: int
#     coord: Coordinate
#     purpose: str

#     def __init__(self, end_time, duration, purpose, coord, apn, maz):
#         self.end_time = end_time
#         self.duration = duration
#         self.purpose = purpose
#         self.coord = coord
#         self.maz = maz
#         self.apn = apn


# class MatsimLeg:
#     ''' Simple representation of MATsim Leg '''
#     mode: str
#     duration: str
#     mode: str

#     def __init__(self, mode: str):
#         self.mode = mode


class MatsimPlan:
    ''' Class creating a MATsim Plan, from a MAG agent.
        Agent must have all properties, and mapping must include agents MAZ.
        Mapping must be a 4-column Df with: [maz, apn, x, y] '''
    person_id: int
    mag_pnum: int
    mag_hhid: int
    home_maz: int
    home_apn: str
    home_coord: coordinate
    mapping: pd.DataFrame
    conv: MagConvIndex
    events: Tuple[T, ...]

    def __init__(self, agent: MagAgent, mapping: pd.DataFrame):
        self.mapping = mapping
        self.person_id = agent.p_num
        self.mag_pnum = agent.mag_pnum
        self.mag_hhid = agent.mag_hhid
        home = self.random_apn(agent.home_maz)
        self.home_maz = home.iloc[0, 0]
        self.home_apn = home.iloc[0, 1]
        self.home_coord = coordinate(x=home.iat[0, 2], y=home.iat[0, 3])
        self.events = tuple([])
        self.create_plan(agent)

    def random_apn(self, maz: int) -> str:
        ''' Get a random APN for a given MAZ. '''
        # TODO: Improve this
        return self.mapping.loc[self.mapping['maz'] == maz].sample()

    def single(self, trip: Tuple[T, ...]):
        ''' '''
        initial_act = self.initial_act_creation(trip)
        # Currently not using duration because MATsim doesn't require it
        # duration = trip[self.conv.leg_time]
        final_act = self.final_events_creation(trip)
        self.events = tuple([*initial_act, *final_act])

    def multiple(self, trips: List[Tuple[T, ...]]):
        initial_act = self.initial_act_creation(trips[0])

        middle_events = list()
        for trip in trips[0:-1]:
            middle_events.extend(self.standard_event_creation(trip))

        final_events = self.final_events_creation(trip)
        self.events = tuple([*initial_act, *middle_events, *final_events])

    def initial_act_creation(self, trip) -> MatsimAct:
        ''' If a MatsimAct is the first Act in a Plan,
            it has an end time but no duration. Purpose = Home. '''
        initial_act = list()
        # if purpose.name != 'home':
        #     initial_act.append(MatsimAct(end_time=0,
        #                                  duration=False,
        #                                  purpose=purpose_encode(0),
        #                                  coord=self.home_coord,
        #                                  apn=self.home_apn,
        #                                  maz=self.home_maz))
        #     initial_act.append(MatsimLeg(Mode(trip[self.conv.mode]).name))

        if purpose_encode[trip[self.conv.orig_type]] is 'home':
            orig_coord = self.home_coord
            orig_apn = self.home_apn
            orig_maz = self.home_maz

        else:
            rand_apn = self.random_apn(trip[self.conv.orig_loc])
            orig_coord = coordinate(rand_apn.iat[0, 2], rand_apn.iat[0, 3])
            orig_apn = rand_apn.iat[0, 1]
            orig_maz = rand_apn.iat[0, 0]

        initial_act.append(MatsimAct(end_time=trip[self.conv.orig_end],
                                     duration=False,
                                     purpose=purpose_encode[0],
                                     coord=orig_coord,
                                     apn=orig_apn,
                                     maz=orig_maz))
        return initial_act

    def final_events_creation(self, trip) -> Tuple[MatsimLeg, MatsimAct]:
        ''' If a MatsimAct is the last Act in a Plan,
            it has no end time and no duration. Purpose = Home. '''
        final_act = list()
        final_act.append(MatsimLeg(mode_encode[trip[self.conv.mode]]))
        dest = self.random_apn(trip[self.conv.dest_loc])
        final_act.append(MatsimAct(end_time=trip[self.conv.dest_dur]+trip[self.conv.dest_start],
                                   duration=trip[self.conv.dest_dur],
                                   purpose=purpose_encode[trip[self.conv.dest_type]],
                                   coord=coordinate(dest.iat[0, 2],
                                                    dest.iat[0, 3]),
                                   apn=dest.iat[0, 1],
                                   maz=dest.iat[0, 0]))
        # if purpose_encode.name != 'home':
        #     final_act.append(MatsimLeg(Mode(trip[self.conv.mode]).name))
        #     final_act.append(MatsimAct(end_time=60*60*24,
        #                                duration=60*60,
        #                                purpose=Purpose(0),
        #                                coord=self.home_coord,
        #                                apn=self.home_apn,
        #                                maz=self.home_maz))
        return final_act

    def standard_event_creation(self, trip):
        ''' Give actor APNs and coordinate for trips based off MAZ/trip type'''
        leg = MatsimLeg(mode_encode[trip[self.conv.mode]])
        dest = self.random_apn(trip[self.conv.dest_loc])
        act = MatsimAct(end_time=trip[self.conv.dest_start]+trip[self.conv.dest_dur],
                        duration=trip[self.conv.dest_dur],
                        purpose=purpose_encode[trip[self.conv.dest_type]],
                        coord=coordinate(dest.iloc[0, 2],
                                         dest.iloc[0, 3]),
                        apn=dest.iloc[0, 1],
                        maz=dest.iloc[0, 0])
        return [leg, act]

    def create_plan(self, agent: MagAgent):
        ''' A MAG travel diary n trips long yeilds:
                (n+1) MATsim Acts, and (n) MATsim Legs '''
        if agent.trip_count == 1:
            self.single(agent.get_trips())
        elif agent.trip_count > 1:
            self.multiple(agent.get_trips())
        else:
            raise ValueError('Agents must have at least one valid Trip')
