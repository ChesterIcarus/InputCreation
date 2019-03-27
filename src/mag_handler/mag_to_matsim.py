from collections import defaultdict
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, T

from util.mapping_db_util import MappingDatabase
from mag_handler.mag_population import MagPopulation, MagHousehold, MagAgent
from mag_handler.matsim_plan import MatsimPlan
from mag_handler.encoded_data_util import MagConvIndex


class MagToMatsim:
    conv: MagConvIndex = None

    def __init__(self, conv: MagConvIndex):
        self.conv = conv
        # Sets it for all objects of type MatsimPlan
        MatsimPlan.conv = self.conv

    def convert(self, population: MagPopulation,
                mapping_database: MappingDatabase) -> List[MatsimPlan]:
        matims_plans = list()
        household: MagHousehold
        for household in list(population.households.values()):
            agent: MagAgent
            for agent in list(household.agents.values()):
                matims_plans.append(MatsimPlan(agent, mapping_database))
        return matims_plans
