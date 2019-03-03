from enum import Enum
from typing import Dict


class MagConvIndex:
    pnum: int
    hhid: int
    orig_loc: int
    orig_end: int
    orig_type: int
    mode: int
    dest_loc: int
    dest_start: int
    dest_type: int
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


class Purpose(Enum):
    ''' Encode the values in MAG data to an enumerated class '''
    home = 0
    work = 1
    university = 2
    school = 3
    pure_escort = 411
    rideshare = 412
    other_escort = 42
    shopping = 5
    other_maintenence = 6
    ride_share = 4
    food = 7
    breakfast = 71
    lunch = 72
    dinner = 73
    visiting = 8
    other_discretionary = 9
    special_event = 10
    work_related = 15


class Mode(Enum):
    ''' Encode the values in MAG data to an enumerated class '''
    sov = 1
    hov2_driver = 2
    hov3_driver = 3
    hov_passenger = 4
    conv_transit_walk_access = 5
    conv_transit_knr = 6
    conv_transit_pnr = 7
    prem_transit_walk_access = 8
    prem_transit_knr = 9
    prem_transit_pnr = 10
    walk = 11
    bike = 12
    taxi = 13
    school_bus = 14

    def driver(self):
        ''' Return true if the instance of Mode indicates the current 
            agent is a driver, ie. a person driving a car'''
        return (self.value not in [4, 13, 14])


class Coordinate:
    x: float = None
    y: float = None
    system: str = None

    def __init__(self, x=0, y=0, system=0):
        self.x = x
        self.y = y
        self.system = system
