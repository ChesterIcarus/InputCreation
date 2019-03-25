from collections import defaultdict
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, T

from mag_handler.mag_population import MagPopulation, MagHousehold, MagAgent
from mag_handler.matsim_plan import MatsimPlan
from mag_handler.encoded_data_util import MagConvIndex


class MagToMatsim:
    conv: MagConvIndex = None

    def __init__(self, conv: MagConvIndex):
        self.conv = conv
        MatsimPlan.conv = self.conv

    def convert(self, population: MagPopulation, mapping: pd.DataFrame) -> List[MatsimPlan]:
        matims_plans = list()
        # Use dask parrellization here
        household: MagHousehold
        for household in list(population.households.values()):
            agent: MagAgent
            for agent in list(household.agents.values()):
                matims_plans.append(MatsimPlan(agent, mapping))
        return matims_plans
