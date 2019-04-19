import numpy as np
import pandas as pd
import dask
import dask.dataframe as dd
import dask.multiprocessing
from typing import List, Dict, Tuple

from mag_handler.encoded_data_util import purpose_encode, mode_encode, MagConvIndex, reverse_mode_encode
from mag_handler.mag_population import MagPopulation
from mag_handler.mag_to_matsim import MagToMatsim
from mag_handler.matsim_plan import MatsimPlan


class MagController:
    ''' Dedicated to reading in MAG-compliant data format (as a csv file) '''
    conv: MagConvIndex

    def __init__(self):
        pass

    def plans_by_col(self, filename, columns, col_dtype=None) -> pd.DataFrame:
        plans = dd.read_csv(filename,
                            usecols=columns,
                            dtype=col_dtype)
        plans = plans.compute(scheduler='threading')
        # This loop filters based on whether the agent is the driver or not
        # passenger = [reverse_mode_encode['hov_passenger'],
        #              reverse_mode_encode['taxi'],
        #              reverse_mode_encode['school_bus']]
        only_cars = [0, 1, 2, 3]
        plans = plans[plans['mode'].isin(only_cars)]
        plans['mode'] = 0
        plans.sort_values(by='hhid', inplace=True)
        return plans

    def plans_to_population(self, plans) -> MagPopulation:
        pop = MagPopulation()
        pop.define_agents(plans)
        return pop
