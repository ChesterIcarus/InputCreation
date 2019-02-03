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
        for household in list(population.households.values()):
            for agent in list(household.agents.values()):
                matims_plans.append(MatsimPlan(agent.p_num))
                matims_plans[-1].create_plan(agent)
        return matims_plans
