from collections import defaultdict
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, T
from random import shuffle

from util.mapping_db_util import MappingDatabase
from mag_handler.mag_population import MagPopulation, MagHousehold, MagAgent
from mag_handler.matsim_plan import MatsimPlan
from mag_handler.encoded_data_util import MagConvIndex

from mag_handler.fast.matsim_plan import FastMatsimPlan
import dask.multiprocessing
from dask import compute, delayed, visualize


@dask.delayed
def delayed_fastplan(population: pd.DataFrame):
    hhids = lambda raw_plans: raw_plans.groupby(['hhid']).apply(
                lambda house: house.groupby(['pnum']).apply(
                    lambda agent: FastMatsimPlan(agent)
                )
            )
    return hhids(population)

class MagToMatsim:
    def __init__(self, database: MappingDatabase,
                 map_dict: pd.DataFrame = None):
        # Sets it for all objects of type MatsimPlan
        MatsimPlan.mapping_db = database
        try:
            map_sel = {k: [0, len(map_dict[k])-1]
                                for k in map_dict.keys()}
            FastMatsimPlan.mapping_select = map_sel
            FastMatsimPlan.mapping = mapping
        except Exception:
            pass

    def from_pyobj(self, population: MagPopulation) -> List[MatsimPlan]:
        matims_plans = list()
        household: MagHousehold
        for household in list(population.households.values()):
            agent: MagAgent
            for agent in list(household.agents.values()):
                matims_plans.append(MatsimPlan(agent))
        return matims_plans

    def from_df(self, population: pd.DataFrame):
        matims_plans = list()
        to_fastplan = lambda raw_plans: raw_plans.groupby(['hhid']).apply(
            lambda house: house.groupby(['pnum']).apply(
                lambda agent: FastMatsimPlan(agent)
            )
        )
        plans = to_fastplan(population)
        return list(plans)

    def from_df_mp(self, population: pd.DataFrame, processes=60):
        dask.config.set(scheduler='processes')
        unique_hhids = population['hhid'].unique()
        hhid_chunks = np.array_split(unique_hhids, processes)
        hhid_chunks = [(chunk.min(), chunk.max()) for chunk in hhid_chunks]
        pop_chunks = list()
        for chunk in hhid_chunks:
            pop_chunk = population[(population['hhid'] >= chunk[0]) &
                                   (population['hhid'] <= chunk[1])]
            pop_chunks.append(pop_chunk)
        return pd.concat(compute(*map(delayed_fastplan, pop_chunks)))

