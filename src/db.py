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

city_db_path = 'index/cities.dat'
street_db_path = 'index/streets.dat'
locality_db_path = 'index/localities.dat'
number_db_path = 'index/numbers.dat'
cities_post_index_path = 'index/cities_post_index.dat'
streets_insee_index_path = 'index/streets_insee_index.dat'
localities_insee_index_path = 'index/localities_insee_index.dat'
numbers_locality_index_path = 'index/numbers_locality_index.dat'
numbers_geohash_index_path = 'index/numbers_geohash_index.dat'

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
        self.cities = self.load_data(city_db_path, dtype=city_dtype)
        self.streets = self.load_data(street_db_path, dtype=street_dtype)
        self.localities = self.load_data(locality_db_path,
                                         dtype=locality_dtype)
        self.numbers = self.load_data(number_db_path, dtype=number_dtype)

        # indices
        self.cities_post_index = self.load_data(cities_post_index_path)
        self.streets_insee_index = self.load_data(streets_insee_index_path)
        self.localities_insee_index = self.load_data(
            localities_insee_index_path)
        self.numbers_locality_index = self.load_data(
            numbers_locality_index_path)
        self.numbers_geohash_index = self.load_data(
            numbers_geohash_index_path)

    def load_data(self, file_path, dtype='int32'):
        return np.memmap(file_path, dtype=dtype)
