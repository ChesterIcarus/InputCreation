from collections import defaultdict
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, T

from mag_handler.mag_population import MagPopulation, MagHousehold, MagAgent
from mag_handler.matsim_plan import MatsimPlan
from mag_handler.encoded_data_util import MagConvIndex


class MagToMatsim:
    mag_indexes: Dict[str, int]

    def __init__(self, conv: MagConvIndex):
        self.conv = conv
        MatsimPlan.conv = self.conv

    def convert(self, population: MagPopulation) -> List[MatsimPlan]:
        matims_plans = list()
        household: MagHousehold
        for household in list(population.households.values()):
            # Need to assign household APN here
            agent: MagAgent
            for agent in list(household.agents.values()):
                mat_plan = MatsimPlan(agent)
                matims_plans.append(mat_plan)
        return matims_plans

    def home_creation(self, maz, mapping):
        return 0
