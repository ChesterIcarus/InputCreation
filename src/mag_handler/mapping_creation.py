from typing import List, Dict, T
from collections import defaultdict
import numpy as np
import pandas as pd


class MappingCreation:
    columns: List[str] = ['maz', 'apn', 'x', 'y']
    mappings: defaultdict = None

    def __init__(self):
        self.mappings = defaultdict(int)

    def read_csv(self, filename):
        data = pd.read_csv(filename,
                           usecols=self.columns)
        data['rand_id'] = 0
        return data

    def zone_counts(self, data: pd.DataFrame) -> Dict[int, int]:
        zones = data['maz'].value_counts().to_dict()
        return zones

    def zone_mappings(self, row) -> int:
        tmp = self.mappings[row[0]]
        self.mappings[row[0]] += 1
        return tmp

    def process(self, data: pd.DataFrame):
        data['rand_id'] = data.apply(self.zone_mappings, axis=1)
        return data
