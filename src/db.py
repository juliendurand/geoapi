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
import references as ref
import os

CITY_DB_PATH = os.path.join(ref.INDEX_DIR, ref.CITY_DB)
STREET_DB_PATH = os.path.join(ref.INDEX_DIR, ref.STREET_DB)
LOCALITY_DB_PATH = os.path.join(ref.INDEX_DIR, ref.LOCALITY_DB)
NUMBER_DB_PATH = os.path.join(ref.INDEX_DIR, ref.NUMBER_DB)

CITIES_POST_INDEX_PATH = os.path.join(ref.INDEX_DIR, ref.CITIES_POST_INDEX)
STREETS_INSEE_INDEX_PATH = os.path.join(ref.INDEX_DIR, ref.STREETS_INSEE_INDEX)
LOCALITIES_INSEE_INDEX_PATH = os.path.join(ref.INDEX_DIR,
                                           ref.LOCALITIES_INSEE_INDEX)
NUMBERS_LOCALITY_INDEX_PATH = os.path.join(ref.INDEX_DIR,
                                           ref.NUMBERS_LOCALITY_INDEX)
NUMBERS_GEOHASH_INDEX_PATH = os.path.join(ref.INDEX_DIR,
                                          ref.NUMBERS_GEOHASH_INDEX)


city_dtype = np.dtype([
    ('code_insee', 'a5'),
    ('code_post', 'a5'),
    ('nom_commune', 'a45'),
    ('lon', 'int32'),
    ('lat', 'int32'),
])

street_dtype = np.dtype([
    ('street_id', 'int32'),
    ('code_insee', 'a5'),
    ('code_post', 'a5'),
    ('nom_voie', 'a32'),
])

# 'lieu-dit' in french
locality_dtype = np.dtype([
    ('locality_id', 'int32'),
    ('code_insee', 'a5'),
    ('code_post', 'a5'),
    ('nom_ld', 'a80'),
])

number_dtype = np.dtype([
    ('street_id', 'int32'),
    ('locality_id', 'int32'),
    ('number', 'int16'),
    ('rep', 'int8'),
    ('geohash', 'uint64'),
])


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
