from typing import Dict, Tuple, List, T
import MySQLdb as sql
import MySQLdb.connections as connections
from warnings import warn
from random import randrange
import json

from util.db_util import DatabaseHandle


class MappingDatabase(DatabaseHandle):
    zone_count: Dict[int, int] = None

    def __init__(self, params: Dict[str, str] = None, handle=None):
        super().__init__(params=params, handle=handle)
        self.zone_count = None

    def load_zone_counts(self, filepath):
        with open(filepath, 'r') as handle:
            zones = json.load(handle)
        keys = list(zones)
        for key in keys:
            zones[int(key)] = zones[key]
            del zones[key]
        self.zone_count = zones

    def get_apn(self, maz: int) -> [int, str, float, float]:
        rand_id = randrange(0, self.zone_count[maz])
        exec_str = f''' SELECT 
                            maz, apn, x, y
                        from 
                            {self.db}.{self.table}
                        WHERE
                            maz = {maz}
                        AND
                            rand_id = {rand_id}'''
        self.cursor.execute(exec_str)
        return self.cursor.fetchall()[0]
