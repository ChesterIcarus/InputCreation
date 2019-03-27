from enum import Enum
from typing import Dict
from collections import namedtuple


mode_encode = {
    0: 'car', 1: 'sov', 2: 'hov2_driver', 3: 'hov3_driver',
    4: 'car', 5: 'conv_transit_walk_access', 6: 'conv_transit_knr',
    7: 'conv_transit_pnr', 8: 'prem_transit_walk_access',
    9: 'prem_transit_knr', 10: 'prem_transit_pnr', 11: 'walk',
    12: 'bike', 13: 'car', 14: 'car'
}
purpose_encode = {
    0: 'home',
    1: 'work',
    2: 'university',
    3: 'school',
    411: 'pure_escort',
    412: 'rideshare',
    42: 'other_escort',
    5: 'shopping',
    6: 'other_maintenence',
    4: 'ride_share',
    7: 'food',
    71: 'breakfast',
    72: 'lunch',
    73: 'dinner',
    8: 'visiting',
    9: 'other_discretionary',
    10: 'special_event',
    15: 'work_related'
}

coordinate = namedtuple('coordinate', ['x', 'y'])


class MagConvIndex:
    pnum: int
    hhid: int
    orig_loc: int
    orig_end: int
    orig_type: int
    mode_encode: int
    dest_loc: int
    dest_start: int
    dest_type: int
    dest_dur: int
    leg_time: int

    def __init__(self, mag_indexes: Dict[str, int]):
        self.pnum = mag_indexes['pnum']
        self.hhid = mag_indexes['hhid']
        self.orig_loc = mag_indexes['origMaz']
        self.orig_end = mag_indexes['finalDepartMinute']
        self.orig_type = mag_indexes['origPurp']
        self.mode = mag_indexes['mode']
        self.dest_loc = mag_indexes['destMaz']
        self.dest_start = mag_indexes['finalArriveMinute']
        self.dest_type = mag_indexes['destPurp']
        self.dest_dur = mag_indexes['activityMinutesAtDest']
        self.leg_time = mag_indexes['finalTravelMinutes']


# class Coordinate:
#     x: float = None
#     y: float = None
#     system: str = None

#     def __init__(self, x=0, y=0, system=0):
#         self.x = x
#         self.y = y
#         self.system = system
