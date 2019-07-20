from getpass import getpass
from sys import argv

from network_util.parcel_MAZ_db_gen import ParcelDbGen
from util.db_util import DatabaseHandle

params = {'user': 'root', 'password': None,
            'db': 'icarus_postsim', 'host':'localhost',
          'tables': {'parcelMaz': {'schema': ['MAZ VARCHAR(24)',
                                              'APN VARCHAR(9)',
                                              'coord_x DOUBLE',
                                              'coord_y DOUBLE'] }
           }
          }

params['password'] = getpass()
if (len(argv) == 0):
    raise ValueError('Must enter file in command line argument')
db = DatabaseHandle(params)
db.create_table('parcelMaz')
parcel_gen = ParcelDbGen(db)
parcel_gen.read_input('../../data/mag_to_matsim_required_aux/full_maricop_parcel_coord_by_MAZ.json')
