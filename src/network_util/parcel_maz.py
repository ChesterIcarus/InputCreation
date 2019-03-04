from typing import Dict, List

import json
import pandas as pd


def get_json(filepath):
    data: Dict[int, List[List[int, float, float]]]
    with open(filepath, 'r') as handle:
        data = json.load(handle)

    rows = list()
    for key, value in data.items():
        for val in value:
            rows.append(tuple([int(key), str(val[0]), *val[1:3]]))
    return rows


data = get_json(
    '../../data/mag_to_matsim_required_aux/full_maricop_parcel_coord_by_MAZ.json')
df = pd.DataFrame(data, columns=['maz', 'apn', 'x', 'y'])
df.to_csv('../../data/processed_MAG_data/parcel_by_maz.csv', index=False)
