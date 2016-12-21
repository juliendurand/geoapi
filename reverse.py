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

from utils import haversine
from address import Result
from search import find_index
from utils import geohash, reverse_geohash


def reverse(db, lon, lat):
    min_distance = 50000000  # bigger than Earth's circumference
    match = None
    h = geohash(lon, lat)
    arg = find_index(h, db.numbers_geohash_index, db.numbers['geohash'])
    k = 100  # k-nearest
    lo = max(0, arg - k//2)
    hi = min(db.numbers_geohash_index.size, arg + k//2)
    for hyp in db.numbers_geohash_index[lo:hi]:
        hlon, hlat = reverse_geohash(db.numbers[hyp]['geohash'])
        # Calculate haversine distance to get the real orthonormic distance
        d = haversine(hlon, hlat, lon, lat)
        if d < min_distance:
            min_distance = d
            match = hyp
    return Result.from_plate(db, match, 0, distance=min_distance)


if __name__ == '__main__':
    import main
    db = main.AddressDatabase()
    # in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    in_file = 'data/ADRESSES_PART_GEO_AMABIS_v01072016_out.csv'
    out_file = 'data/ADRESSES_PART_GEO_AMABIS_v01072016_out_reverse_julien.csv'
    with open(in_file, 'r') as addresses, open(out_file, 'w') as out:
        i = 0
        d = 0
        for line in addresses:
            line = line[:-1]
            if i == 0:
                out.write(line+';locality;number;street;code_post;city;code_insee;country;distance;lon;lat;\n')
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
            # print(values[32], values[33])
            try:

                lon = float(values[32])
                lat = float(values[33])
                address = reverse(db, lon, lat).to_address()
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
                d += address['distance']
            except Exception as e:
                print(e)
            out.write(";".join(map(str, values))+'\n')
            i += 1
        print(i, ' lines')
        print(d/i, ' mean distance')
