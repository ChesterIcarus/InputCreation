import dill
from getpass import getpass

from mag_handler.population_util import PopulationUtil
from util.db_util import DatabaseHandle

pass__ = getpass()
params = {'user': 'root', 'db': 'example',
          'host': 'localhost', 'password': pass__}
example = PopulationUtil(
    dill.load(open('data/interim/population.dill', 'rb')))
example.create_db(DatabaseHandle(**params))
