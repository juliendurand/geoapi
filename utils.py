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

from math import pi, cos, sin, tan, asin, sqrt, log, exp

import mmap
import pyproj

DEGREE_TO_INT_SCALE = 10000000


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default or to_type()


def degree_to_int(angle):
    return int(angle * DEGREE_TO_INT_SCALE)


def int_to_degree(value):
    return value / DEGREE_TO_INT_SCALE


def geohash(lon, lat):
    lon = degree_to_int(lon + 180)
    lat = degree_to_int(lat + 90)
    lonbin = bin(lon)[2:].zfill(32)
    latbin = bin(lat)[2:].zfill(32)
    b = ''.join([val for pair in zip(lonbin, latbin) for val in pair])
    return int(b, 2)


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
    lon1 *= 0.01745329252
    lat1 *= 0.01745329252
    lon2 *= 0.01745329252
    lat2 *= 0.01745329252
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    m = 6367000 * c
    return m


def find(x, values, string=False):
    lo = 0
    hi = len(values)
    while lo < hi:
        mid = (lo + hi) // 2
        midval = values[mid]
        if string:
            midval = midval.decode('UTF-8')
        if midval < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


# TODO : remove because not useful anymore
def find_all(x, values):
    pos = find(x, values)
    size = values.size
    while pos < size:
        if values[pos] != x:
            break
        yield pos
        pos += 1


def find_index(x, index, values, string=False):
    lo = 0
    hi = len(index)
    while lo < hi:
        mid = (lo + hi) // 2
        idx = index[mid]
        if (idx > 100000000):
            print("IDX ERROR", x, lo, hi, mid, idx, string)
        midval = values[idx]
        if string:
            midval = midval.decode('UTF-8')
        if midval < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


def find_all_from_index(x, index, values, string=False):
    idx = find_index(x, index, values, string)
    n = len(index)
    while idx < n:
        pos = index[idx]
        value = values[pos]
        if string:
            value = value.decode('UTF-8')
        if value != x:
            break
        yield pos
        idx += 1


wgs84 = pyproj.Proj(init='EPSG:4326')
lambert93 = pyproj.Proj(init='EPSG:2154')


def conv_lambert93_to_wsg84(lon, lat):
    return pyproj.transform(lambert93, wgs84, lon, lat)


def conv_wsg84_to_lambert93(lon, lat):
    return pyproj.transform(wgs84, lambert93, lon, lat)


# TODO remove unused functions below

def isometric_latitude(lat, e):
    esl = e * sin(lat)
    return log(tan(pi / 4 + lat / 2) * pow((1 - esl) / (1 + esl), e / 2))


def conv_wsg84_to_lambert93_mine(lon_deg, lat_deg,
        n = 0.755525978809006,  # projection exponent
        c = 11099578.2774377,  # projection constant (m)
        e = 0.0818191910428158,  # first eccentricity of ellipsoid
        lon_orig = 3 * pi / 180,  # longitude of origin (rad)
        xpole = 700000.0,  # x coordinate of pole (m)
        ypole = 6600000.0,  # y coordinate of pole (m)
        ):

    lon = lon_deg * pi / 180
    lat = lat_deg * pi / 180
    lat_iso = isometric_latitude(lat, e)
    c_e_lat_iso = c * exp(-n * lat_iso)
    n_lon_delta = n * (lon - lon_orig)
    x = xpole + c_e_lat_iso * sin(n_lon_delta)
    y = ypole - c_e_lat_iso * cos(n_lon_delta)

    return (int(x), int(y), )
