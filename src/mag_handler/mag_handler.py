import numpy as np
import pandas as pd
from typing import List, Dict, Tuple

from encoded_data_util import Purpose, Mode, MagConvIndex
from mag_population import MagPopulation
from mag_to_matsim import MagToMatsim
from matsim_plan import MatsimPlan


class MagHandler:
    ''' Dedicated to reading in MAG-compliant data format (as a csv file) '''
    conv: MagConvIndex

    def __init__(self, mag_indexes):
        self.conv = MagConvIndex(mag_indexes)

    def plans_by_col(self, filename, columns, col_dtype=None) -> pd.DataFrame:
        plans = pd.read_csv(filename, usecols=columns, dtype=col_dtype)
        mask = list()
        # This loop filters based on w/e the agent is the driver or not
        for row in plans.itertuples():
            mask.append(Mode(row[7]).driver())
        plans = plans[pd.Series(mask)]
        return plans

    def plans_to_population(self, plans) -> MagPopulation:
        pop = MagPopulation()
        pop.define_agents(plans, self.conv)
        return pop

    def population_to_matsim(self, population: MagPopulation) -> List[MatsimPlan]:
        mag_to_mat = MagToMatsim(self.conv)
        return mag_to_mat.convert(population)
