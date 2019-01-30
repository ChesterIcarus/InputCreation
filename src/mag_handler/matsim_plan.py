from typing import Dict, List, Tuple, T

from mag_handler.encoded_data_util import MagConvIndex
from mag_handler.mag_population import MagAgent


class MatsimAct:
    end_time: T
    duration: T
    coord: Tuple[float, float]
    maz: int
    type_: str

    def __init__(self, end, dur, type_, coord=None, maz=None):
        ''' If a MatsimAct is the first Act in a Plan, end_tim is type str.
                Else, it is False. Only initial Acts have an end_time in Matsim.
            If both end_time and duration are False, it is the last Act in a Plan
        '''
        self.end_time = end
        self.duration = dur
        self.type_ = type_
        self.coord = coord
        self.maz = maz


class MatsimLeg:
    mode: str
    duration: str

    def __init__(self, mode, dur):
        self.mode = mode
        if dur == '':
            self.duration = None
        else:
            self.duration = dur


class MatsimPlan:
    id_: int
    plan: Tuple[T]
    conv: MagConvIndex

    def __init__(self, id_):
        self.id_ = id_

    def single(self, trip: Tuple[T, ...], incl_leg_t=False):
        orig_list = [trip[self.conv.orig_end],
                     False, trip[self.conv.orig_type]]
        orig_act = MatsimAct(*orig_list, maz=trip[self.conv.orig_loc])

        leg_mode = trip[self.conv.mode]
        if incl_leg_t:
            leg_dur = trip[self.conv.leg_time]
        else:
            leg_dur = ''
        leg = MatsimLeg(leg_mode, leg_dur)

        dest_list = [False, False, trip[self.conv.dest_type]]
        dest_act = MatsimAct(*dest_list, maz=trip[self.conv.dest_loc])
        self.plan = tuple([orig_act, leg, dest_act])

    def multiple(self, trips: List[Tuple[T, ...]], incl_leg_t=False):
        trip_list = list()
        orig_list = [trips[0][self.conv.orig_end],
                     False, trips[0][self.conv.orig_type]]
        trip_list.append(
            MatsimAct(*orig_list, maz=trips[0][self.conv.orig_loc]))

        for trip in trips[0:-1]:
            if incl_leg_t:
                leg_dur = trip[self.conv.leg_time]
            else:
                leg_dur = ''
            trip_list.append(MatsimLeg(trip[self.conv.mode], leg_dur))

            dest_list = [False, trip[self.conv.dest_dur],
                         trip[self.conv.dest_type]]
            trip_list.append(
                MatsimAct(*dest_list, maz=trip[self.conv.dest_loc]))
        if incl_leg_t:
            leg_dur = trip[self.conv.leg_time]
        else:
            leg_dur = ''
        trip_list.append(MatsimLeg(trips[-1][self.conv.mode], leg_dur))
        dest_list = [False, False, trips[-1][self.conv.dest_type]]
        trip_list.append(MatsimAct(*dest_list, maz=trip[self.conv.dest_loc]))
        self.plan = tuple(trip_list)

    def create_plan(self, agent: MagAgent):
        self.plan = None
        if agent.trips == 1:
            self.single(agent.get_trips())
        elif agent.trips > 1:
            self.multiple(agent.get_trips())
        else:
            raise ValueError('Agents must have at least one valid Trip')
        self.plan = tuple(self.plan)
