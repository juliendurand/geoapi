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

import datatypes as dtp
import references as ref

CITY_DB_PATH = ref.CITY_DB_PATH
STREET_DB_PATH = ref.STREET_DB_PATH
LOCALITY_DB_PATH = ref.LOCALITY_DB_PATH
NUMBER_DB_PATH = ref.NUMBER_DB_PATH

CITIES_POST_INDEX_PATH = ref.CITIES_POST_INDEX_PATH
STREETS_INSEE_INDEX_PATH = ref.STREETS_INSEE_INDEX_PATH
LOCALITIES_INSEE_INDEX_PATH = ref.LOCALITIES_INSEE_INDEX_PATH
NUMBERS_LOCALITY_INDEX_PATH = ref.NUMBERS_LOCALITY_INDEX_PATH
NUMBERS_GEOHASH_INDEX_PATH = ref.NUMBERS_GEOHASH_INDEX_PATH

city_dtype = dtp.city_dtype
street_dtype = dtp.street_dtype
locality_dtype = dtp.locality_dtype
number_dtype = dtp.number_dtype


class AddressDatabase:

    def __init__(self):
        # data tables
        self.cities = self.load_data(CITY_DB_PATH, dtype=city_dtype)
        self.streets = self.load_data(STREET_DB_PATH, dtype=street_dtype)
        self.localities = self.load_data(LOCALITY_DB_PATH,
                                         dtype=locality_dtype)
        self.numbers = self.load_data(NUMBER_DB_PATH, dtype=number_dtype)

        # indices
        self.cities_post_index = self.load_data(CITIES_POST_INDEX_PATH)
        self.streets_insee_index = self.load_data(STREETS_INSEE_INDEX_PATH)
        self.localities_insee_index = self.load_data(
            LOCALITIES_INSEE_INDEX_PATH)
        self.numbers_locality_index = self.load_data(
            NUMBERS_LOCALITY_INDEX_PATH)
        self.numbers_geohash_index = self.load_data(
            NUMBERS_GEOHASH_INDEX_PATH)

    def load_data(self, file_path, dtype='int32'):
        return np.memmap(file_path, dtype=dtype)
