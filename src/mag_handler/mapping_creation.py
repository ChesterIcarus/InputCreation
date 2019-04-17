from typing import List, Dict, T
from collections import defaultdict
import numpy as np
import pandas as pd
import dask.dataframe as dd
import dask.multiprocessing
from numba import njit


class MappingCreation:
    columns: List[str] = ['maz', 'apn', 'x', 'y']
    mappings: defaultdict = None

    def __init__(self):
        self.mappings = defaultdict(int)

    def read_csv(self, filename):
        # if columns is not None:
        #     self.columns = [col.split(' ')[0] for col in columns]
        apns = dd.read_csv(filename, usecols=self.columns)
        apns['rand_id'] = 0
        self.apns = apns.compute(scheduler='threads')
        zone_counts = apns['maz'].value_counts()
        self.zone_counts = zone_counts.compute(scheduler='threads').to_dict()

    def zone_mappings(self, row) -> int:
        tmp = self.mappings[row[0]]
        self.mappings[row[0]] += 1
        return tmp

    def process(self):
        data['rand_id'] = data.apply(self.zone_counts, axis=1)
        return data

# @njit(parallel=True, fastmath=True)
# def exposure_njit(n: np.ndarray, exposures: np.ndarray,
#                   cdf: np.ndarray, god_factor: np.ndarray):
#     percents = np.zeros_like(exposures)
#     for i in prange(n.size):
#         high = cdf[ceil(exposures[i])]
#         low = cdf[floor(exposures[i])]
#         percents[i] = low + ((high - low) *
#                              (exposures[i] - floor(exposures[i])))
#     return n[percents > god_factor]
