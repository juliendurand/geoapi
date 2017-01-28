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

from enum import Enum
import json

import iris
from utils import int_to_degree, reverse_geohash, find, conv_wsg84_to_lambert93


class ResultQuality(Enum):
    ERROR = 0
    PLATE = 1
    NUMBER = 2
    STREET = 3
    CITY = 4
    ZIP = 5


class ResultQualityEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ResultQuality):
            return obj.value
        return json.JSONEncoder.default(self, obj)


class Result():

    def __init__(self, quality):
        self.quality = quality
        self.error_msg = ''
        self.locality = ''
        self.number = ''
        self.street = ''
        self.city = ''
        self.code_post = ''
        self.code_insee = ''
        self.code_iris = ''
        self.country = 'France'
        self.lon = ''
        self.lat = ''
        self.distance = ''
        self.score = ''
        self.time = ''

    @classmethod
    def from_error(cls, error_msg):
        r = cls(ResultQuality.ERROR)
        r.error_msg = error_msg
        return r

    @classmethod
    def from_plate(cls, db, number_idx, score, distance=None):
        r = cls(ResultQuality.PLATE)

        r.set_from_number(db, number_idx)
        r.score = round(score, 4)

        if distance:
            r.distance = round(distance, 2)  # precision to 1 cm

        return r

    @classmethod
    def from_interpolated(cls, db, number, street_id, lon, lat):
        r = cls(ResultQuality.NUMBER)

        street = db.streets[street_id]
        code_insee = street['code_insee']
        city_arg = find(code_insee, db.cities['code_insee'])
        city = db.cities[city_arg]

        r.number = int(number)
        r.street = street['nom_voie'].decode('UTF-8')
        r.code_post = street['code_post'].decode('UTF-8')
        r.city = city['nom_commune'].decode('UTF-8')
        r.code_insee = code_insee.decode('UTF-8')
        r.lon = lon
        r.lat = lat
        x, y = conv_wsg84_to_lambert93(lon, lat)
        r.x = x
        r.y = y
        r.code_iris = iris.get_iris(r.code_insee, x=x, y=y)

        return r

    @classmethod
    def from_street(cls, db, number_idx):
        r = cls(ResultQuality.STREET)

        r.set_from_number(db, number_idx)
        r.number = ''

        return r

    @classmethod
    def from_city(cls, db, code_insee, code_post=None):
        r = cls(ResultQuality.CITY)

        city_arg = find(code_insee, db.cities['code_insee'], string=True)
        city = db.cities[city_arg]

        r.city = city['nom_commune'].decode('UTF-8')
        r.code_insee = code_insee
        r.code_post = code_post or city['code_post'].decode('UTF-8')
        r.code_iris = iris.get_iris(code_insee) or ''
        r.lon = int_to_degree(city['lon'])
        r.lat = int_to_degree(city['lat'])
        x, y = conv_wsg84_to_lambert93(r.lon, r.lat)
        r.x = x
        r.y = y

        return r

    @classmethod
    def from_code_post(cls, db, code_post):
        r = cls(ResultQuality.ZIP)

        # FIXME : return the centroid of the zip
        city_arg = find(code_post, db.cities['code_post'], string=True)
        city = db.cities[city_arg]

        r.code_post = code_post
        r.lon = int_to_degree(city['lon'])
        r.lat = int_to_degree(city['lat'])
        x, y = conv_wsg84_to_lambert93(r.lon, r.lat)
        r.x = x
        r.y = y

        return r

    def set_time(self, time):
        self.time = round(time, 6)

    def set_from_number(self, db, number_idx):
        n = db.numbers[number_idx]
        locality_id = n['locality_id']
        street_id = n['street_id']
        street = db.streets[street_id]
        code_insee = street['code_insee']
        city_arg = find(code_insee, db.cities['code_insee'])
        city = db.cities[city_arg]
        locality = db.localities[locality_id]
        locality_name = locality['nom_ld'].decode('UTF-8')
        if not locality_name:
            self.number = int(n['number'])
            self.street = street['nom_voie'].decode('UTF-8')
            self.code_post = street['code_post'].decode('UTF-8')
        else:
            self.locality = locality['nom_ld'].decode('UTF-8')
            self.code_post = locality['code_post'].decode('UTF-8')
        self.city = city['nom_commune'].decode('UTF-8')
        self.code_insee = code_insee.decode('UTF-8')
        lon, lat = reverse_geohash(n['geohash'])
        self.lon = lon
        self.lat = lat
        x, y = conv_wsg84_to_lambert93(lon, lat)
        self.x = x
        self.y = y
        self.code_iris = iris.get_iris(self.code_insee, x, y)

    def to_plain_address(self):
        address = []
        if self.locality:
            address.append(self.locality)
        elif self.street:
            address.append(str(self.number) + ' ' + self.street)
        address.append(self.code_post + ' ' + self.city)
        address.append(self.country)
        map(str.strip, address)
        return address

    def to_address(self):
        self.text = self.to_plain_address()
        return self.__dict__

    def to_json(self):
        return json.dumps(self.to_address(), cls=ResultQualityEncoder,
                          sort_keys=True, indent=4)
