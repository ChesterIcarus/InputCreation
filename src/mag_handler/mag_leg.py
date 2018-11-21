from encoded_data_util import Purpose, Mode


class MagLeg:
    orig_maz: int = 0
    dest_maz: int = 0
    orig_purp: Purpose = None
    dest_purp: Purpose = None
    mode: Mode = None
    final_depart_minute: float = 0.0
    trip_distance: float = 0.0
    final_travel_minute: float = 0.0
    final_arrival_minute: float = 0.0
    activity_minutes_at_dest: float = 0.0
    prn_park_maz: int = 0

    def __init__(self):
        pass
