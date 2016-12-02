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
from utils import int_to_degree


class ResultQuality(Enum):
    ERROR = 0
    PLATE = 1
    NUMBER = 2
    STREET = 3
    CITY = 4
    ZIP = 5


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
        self.country = 'France'
        self.lon = ''
        self.lat = ''
        self.distance = ''
        self.time = ''

    @classmethod
    def from_error(cls, error_msg):
        r = cls(ResultQuality.ERROR)
        r.error_msg = error_msg
        return r

    @classmethod
    def from_plate(cls, db, number_idx, distance=None):
        r = cls(ResultQuality.PLATE)

        n = db.numbers[number_idx]
        locality_id = n['locality_id']
        street_id = n['street_id']
        street = db.streets[street_id]

        code_insee = street['code_insee']
        city_arg = db.cities['code_insee'].searchsorted(code_insee)
        city = db.cities[city_arg]
        locality = db.localities[locality_id]
        locality_name = locality['nom_ld'].decode('UTF-8')
        if not locality_name:
            r.number = int(n['number'])
            r.street = street['nom_voie'].decode('UTF-8')
            r.code_post = street['code_post'].decode('UTF-8')
        else:
            r.number = ''
            r.street = ''
            r.code_post = locality['code_post'].decode('UTF-8')
        r.city = city['nom_commune'].decode('UTF-8')
        r.code_insee = code_insee.decode('UTF-8')
        r.lon = int_to_degree(n['lon'])
        r.lat = int_to_degree(n['lat'])

        if distance:
            r.distance = round(distance, 2)  # precision to 1 cm

        return r

    @classmethod
    def from_interpolated(cls, street_id, lon, lat):
        r = cls(ResultQuality.NUMBER)
        return r

    @classmethod
    def from_street(cls, street_id, lon, lat):
        r = cls(ResultQuality.STREET)
        return r

    @classmethod
    def from_city(cls, code_insee, lon, lat):
        r = cls(ResultQuality.CITY)
        return r

    @classmethod
    def from_code_post(cls, code_post, lon, lat):
        r = cls(ResultQuality.ZIP)
        return r

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
