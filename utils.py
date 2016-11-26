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


def degree_to_int(angle):
    return int(angle*DEGREE_TO_INT_SCALE) if -180 < angle < 180 else 0  # FIXME


def int_to_degree(value):
    return float(value)/DEGREE_TO_INT_SCALE


def b_to_mb(bytes):
    return float(bytes)/1024**2


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
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    m = 6367000 * c
    return m


def soundex(name, len=4):
    # digits holds the soundex values for the alphabet
    # english -> digits = '01230120022455012623010202'
    digits = '01230970072455012683090808'  # french version
    sndx = ''
    fc = ''

    # translate alpha chars in name to soundex digits
    for c in name.upper():
        if c.isalpha():
            if not fc:
                fc = c   # remember first letter
            d = digits[ord(c)-ord('A')]
            # duplicate consecutive soundex digits are skipped
            if not sndx or (d != sndx[-1]):
                sndx += d

    # replace first digit with first alpha character
    sndx = fc + sndx[1:]

    # remove all 0s from the soundex code
    sndx = sndx.replace('0', '')

    # return soundex code padded to len characters
    return (sndx + (len * '0'))[:len]
