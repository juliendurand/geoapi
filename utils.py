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

import mmap
from math import radians, cos, sin, asin, sqrt

DEGREE_TO_INT_SCALE = 10000000


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default or to_type()


def degree_to_int(angle, safe=True):
    if safe:
        return int(angle*DEGREE_TO_INT_SCALE) if -180 <= angle <= 180 else 0  # FIXME
    return int(angle*DEGREE_TO_INT_SCALE)


def int_to_degree(value):
    return value / DEGREE_TO_INT_SCALE


def geohash(lon, lat):
    lon = degree_to_int(lon + 180, safe=False)
    lat = degree_to_int(lat + 90)
    lon = bin(lon)[2:].zfill(32)
    lat = bin(lat)[2:].zfill(32)
    return int(''.join([val for pair in zip(lon, lat) for val in pair]), 2)


def reverse_geohash(h):
    h = bin(h)[2:].zfill(64)
    lon = int_to_degree(int(h[::2], 2)) - 180
    lat = int_to_degree(int(h[1::2], 2)) - 90
    return lon, lat


def b_to_mb(bytes):
    return float(bytes) / 1024**2


def count_file_lines(filename):
    lines = 0
    with open(filename, "r+") as f:
        buf = mmap.mmap(f.fileno(), 0)
        readline = buf.readline
        while readline():
            lines += 1
    return lines


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    m = 6367000 * c
    return m

if __name__ == '__main__':
    # TODO Remove : test only
    import numpy as np
    lon = 2.155987
    lat = 48.935757

    for i in range(1000):
        h = geohash(lon, lat)
        h = np.uint64(h)
        reverse_geohash(h)

    print(lon, lat)
    h = geohash(lon, lat)
    h = np.uint64(h)
    print(h)
    print(*reverse_geohash(h))
