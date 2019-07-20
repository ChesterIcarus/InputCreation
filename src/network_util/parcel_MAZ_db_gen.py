import json
from util.db_util import DatabaseHandle
from getpass import getpass
import sys
from sys import argv


class ParcelDbGen:
    def __init__(self, db_handle: DatabaseHandle):
        if type(db_handle) != DatabaseHandle:
            raise TypeError('Must enter valid DatabaseHandle.')
        self.db_handle: DatabaseHandle = db_handle

    def read_input(self, file, table='parcelMaz', bin_size=0):
        parcels_by_maz = list()
        bin_count = 0
        with open(file, 'r') as handle:
            data = json.load(handle)

        for key in data:
            for entry in data[key]:
                parcels_by_maz.append(
                    (str(entry[0]), str(key),
                     float(entry[1]), float(entry[2])))
                bin_count += 1
            if (bin_size != 0) and (bin_count > bin_size):
                self.db_handle.write_rows(parcels_by_maz, table)
        self.db_handle.write_rows(parcels_by_maz, table)


