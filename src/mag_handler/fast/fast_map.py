from typing import Dict, List, Tuple, T
import dill

class FastMap:
    data: Dict[int, List] = dict()

    def __init__(self, fast_map_filepath, mapping_filepath):
        if fast_map_filepath is not None:
            if self.load(fast_map_filepath):
                return
            else:
                try:
                    self.create(mapping_filepath)
                    self.write(fast_map_filepath)
                except Exception:
                    self.data = None
                    return
        else:
            try:
                self.create(mapping_filepath)
                self.write(fast_map_filepath)
            except Exception:
                self.data = None
                return

    def load(self, filepath):
        try:
            with open(filepath, 'rb') as handle:
                    self.data = dill.load(handle)
            return True
        except Exception:
            return False

    def create(self, mapping_filepath):
        mapping = pd.read_csv(mapping_filepath)
        uniques = mapping['maz'].unique()
        fast_map = {k: (mapping[mapping['maz'] == k].iloc[:, 1:4].itertuples(
                                                               index=False,
                                                               name=None))
                for k in uniques}
        self.data = fast_map

    def write(self, filepath):
        with open(filepath, 'rb') as handle:
            dill.dump(self.data, handle)
