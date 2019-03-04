from typing import Dict, List, Tuple, T

from mag_handler.encoded_data_util import MagConvIndex
from mag_handler.mag_population import MagAgent
from mag_handler.encoded_data_util import Coordinate, Mode, Purpose


class MatsimAct:
    end_time: T
    duration: T
    apn: int
    maz: int
    coord: Coordinate
    purpose: Purpose

    def __init__(self, end_time, duration, purpose: Purpose, coord: Coordinate, apn, maz):
        ''' If a MatsimAct is the first Act in a Plan, end_tim is type str.
                Else, it is False. Only initial Acts have an end_time in Matsim.
            If both end_time and duration are False, it is the last Act in a Plan '''
        self.end_time = end_time
        self.duration = duration
        self.purpose = purpose
        self.coord = coord
        self.maz = maz
        self.apn = apn


class MatsimLeg:
    mode: Mode
    duration: str

    def __init__(self, mode: Mode, duration: str):
        self.mode = mode
        self.duration = duration


class MatsimPlan:
    person_id: int
    mag_pnum: int
    mag_hhid: int
    events: List
    home_coord: Coordinate
    home_apn: int
    conv: MagConvIndex

    def __init__(self, agent: MagAgent):
        self.person_id = agent.p_num
        self.mag_pnum = agent.mag_pnum
        self.mag_hhid = agent.mag_hhid
        self.home_apn = self.generate_apn()

    def generate_apn(self):
        return []

    def single(self, trip: Tuple[T, ...]):
        init_act = self.initial_home_creation(trip)
        mode = Mode(trip[self.conv.mode])
        duration = trip[self.conv.leg_time]
        leg = MatsimLeg(mode, duration)

        final_act = self.final_home_creation(trip)
        self.events = tuple([init_act, leg, final_act])

    def multiple(self, trips: List[Tuple[T, ...]]):
        trip_list = list()
        orig_list = [trips[0][self.conv.orig_end],
                     False, trips[0][self.conv.orig_type]]
        trip_list.append(
            MatsimAct(*orig_list, maz=trips[0][self.conv.orig_loc]))

        for trip in trips[0:-1]:
            self.standard_trip_creation(trip)

        leg_dur = ''
        trip_list.append(MatsimLeg(trips[-1][self.conv.mode], leg_dur))
        dest_list = [False, False, trips[-1][self.conv.dest_type]]
        trip_list.append(MatsimAct(*dest_list, maz=trip[self.conv.dest_loc]))
        self.events = tuple(trip_list)

    def initial_home_creation(self, trip):
        orig_act = MatsimAct(end_time=trip[self.conv.orig_end],
                             duration=False,
                             purpose=trip[self.conv.orig_type],
                             coord=None,
                             apn=None,
                             maz=trip[self.conv.orig_loc])
        return orig_act

    def final_home_creation(self, trip):
        return []

    def standard_trip_creation(self, trip):
        # Give actor APN's and coordinate for trips based off MAZ/trip type
        mode = Mode(trip[self.conv.mode])
        purpose = Purpose(trip[self.conv.orig_type])
        # leg = MatsimLeg(trip[self.conv.mode], ))
        orig_act = MatsimAct(end_time=trip[self.conv.orig_end],
                             duration=False,
                             purpose=purpose,
                             coord=self.home_coord,
                             apn=self.home_apn,
                             maz=trip[self.conv.orig_loc])
        # return orig_act

    def create_plan(self, agent: MagAgent):
        self.plan = None
        if agent.trip_count == 1:
            self.single(agent.get_trips())
        elif agent.trip_count > 1:
            self.multiple(agent.get_trips())
        else:
            raise ValueError('Agents must have at least one valid Trip')
        self.events = tuple(self.events)
