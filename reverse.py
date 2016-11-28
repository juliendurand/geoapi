"""
Copyright (C) 2016 Julien Durand

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import numpy as np
from scipy.spatial import KDTree

from utils import degree_to_int, int_to_degree, haversine
from address import to_address


def kd_tree_index(db):
    data = np.dstack((db.numbers['lon'], db.numbers['lat']))[0]
    kd_tree = KDTree(data, leafsize=10000)
    return kd_tree


def reverse(kd_tree, db, lon, lat):
    # /!\ euclidean distance
    d, idx = kd_tree.query([[degree_to_int(lon), degree_to_int(lat)]], k=10)

    # calculate haversine distance to get the real orthonormic distance
    results = {}
    for hyp in idx[0]:
        pos = db.numbers[hyp]
        hlon = int_to_degree(pos['lon'])
        hlat = int_to_degree(pos['lat'])
        d = haversine(hlon, hlat, lon, lat)
        results[d] = hyp
    idx = sorted(results)[0]
    return to_address(db, results[idx], idx)


if __name__ == '__main__':
    import main
    db = main.AddressDatabase()
    kd_tree = kd_tree_index(db)
    # in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    in_file = 'data/ADRESSES_PART_GEO_AMABIS_v01072016_out.csv'
    with open(in_file, 'r') as addresses:
        i = 0
        for line in addresses:
            line = line[:-1]
            if i == 0:
                print(line+';locality;number;street;code_post;city;code_insee;country;distance;lon;lat;')
                i = 1
                continue
            address = {
                'locality': '',
                'number': '',
                'street': '',
                'code_post': '',
                'city': '',
                'code_insee': '',
                'country': '',
                'lon': '',
                'lat': '',
            }
            values = line[:-1].replace('"', '').split(';')
            print(values[32], values[33])
            try:

                lon = float(values[32])
                lat = float(values[33])
                address = reverse(kd_tree, db, lon, lat)
                values += [
                    address['locality'],
                    address['number'],
                    address['street'],
                    address['code_post'],
                    address['city'],
                    address['code_insee'],
                    address['country'],
                    address['distance'],
                    address['lon'],
                    address['lat'],
                    ]
            except:
                pass
            print(";".join(map(str, values)))
