import numpy as np
import pandas as pd
import dask.dataframe as dd
from typing import List, Dict, Tuple

from mag_handler.encoded_data_util import Purpose, Mode, MagConvIndex
from mag_handler.mag_population import MagPopulation
from mag_handler.mag_to_matsim import MagToMatsim
from mag_handler.matsim_plan import MatsimPlan


class MagController:
    ''' Dedicated to reading in MAG-compliant data format (as a csv file) '''
    conv: MagConvIndex

    def __init__(self, conv: MagConvIndex):
        self.conv = conv

    def plans_by_col(self, filename, columns, col_dtype=None) -> pd.DataFrame:
        plans = dd.read_csv(filename,
                            usecols=columns,
                            dtype=col_dtype)
        mask = list()
        # This loop filters based on w/e the agent is the driver or not
        for row in plans.itertuples():
            mask.append(row[self.conv.mode] not in [4, 13, 14])
        plans = plans[pd.Series(mask)]
        return plans

    def plans_to_population(self, plans) -> MagPopulation:
        pop = MagPopulation(self.conv)
        pop.define_agents(plans)
        return pop
