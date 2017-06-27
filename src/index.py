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

import os
import numpy as np

import db
import utils
import intermediate
import references as ref

INDEX_PATH = ref.INDEX_DIR

CITY_CSV_PATH = intermediate.CITY_CSV_PATH
STREET_CSV_PATH = intermediate.STREET_CSV_PATH
LOCALITY_CSV_PATH = intermediate.LOCALITY_CSV_PATH
NUMBER_CSV_PATH = intermediate.NUMBER_CSV_PATH
REPETITION_JSON_PATH = intermediate.REPETITION_JSON_PATH

CITY_DB_PATH = db.CITY_DB_PATH
STREET_DB_PATH = db.STREET_DB_PATH
LOCALITY_DB_PATH = db.LOCALITY_DB_PATH
NUMBER_DB_PATH = db.NUMBER_DB_PATH

CITIES_POST_INDEX_PATH = db.CITIES_POST_INDEX_PATH
STREETS_INSEE_INDEX_PATH = db.STREETS_INSEE_INDEX_PATH
LOCALITIES_INSEE_INDEX_PATH = db.LOCALITIES_INSEE_INDEX_PATH
NUMBERS_LOCALITY_INDEX_PATH = db.NUMBERS_LOCALITY_INDEX_PATH
NUMBERS_GEOHASH_INDEX_PATH = db.NUMBERS_GEOHASH_INDEX_PATH


def create_dat_file(lst, out_filename, dtype):
    with open(out_filename, 'wb+') as out_file:
        dat_file = np.memmap(out_file, dtype=dtype, shape=(len(lst),))
        dat_file[:] = lst[:]
        dat_file.flush()
    print_results(out_filename, dat_file)


def sort_table(in_filename, dtype, column):
    table = np.memmap(in_filename, dtype=dtype)
    table.sort(order=column)
    print('sorted %s on %s' % (in_filename, column))
    table.flush()


def csv_to_list(in_filename):
    in_file = open(in_filename, 'r+')
    return [tuple(line.strip().split(';')) for line in in_file]


def index_list(in_filename, dtype, column):
    table = np.memmap(in_filename, dtype=dtype)
    indexes_list = np.argsort(table, order=column).astype('int32')
    return indexes_list


def create_info_tables():
    city_list = csv_to_list(CITY_CSV_PATH)
    create_dat_file(city_list, CITY_DB_PATH, db.city_dtype)

    street_list = csv_to_list(STREET_CSV_PATH)
    create_dat_file(street_list, STREET_DB_PATH, db.street_dtype)

    locality_list = csv_to_list(LOCALITY_CSV_PATH)
    create_dat_file(locality_list, LOCALITY_DB_PATH, db.locality_dtype)

    number_list = csv_to_list(NUMBER_CSV_PATH)
    create_dat_file(number_list, NUMBER_DB_PATH, db.number_dtype)

    # Sort tables
    sort_table(CITY_DB_PATH, db.city_dtype, 'code_insee')
    sort_table(NUMBER_DB_PATH, db.number_dtype, 'street_id')


def create_index_tables():
    ind_by_post = index_list(CITY_DB_PATH, db.city_dtype, 'code_post')
    create_dat_file(ind_by_post, CITIES_POST_INDEX_PATH, 'int32')

    st_ind_by_insee = index_list(STREET_DB_PATH, db.street_dtype, 'code_insee')
    create_dat_file(st_ind_by_insee, STREETS_INSEE_INDEX_PATH, 'int32')

    loc_ind_by_insee = index_list(LOCALITY_DB_PATH, db.locality_dtype,
                                  'code_insee')
    create_dat_file(loc_ind_by_insee, LOCALITIES_INSEE_INDEX_PATH, 'int32')

    ind_by_locid = index_list(NUMBER_DB_PATH, db.number_dtype, 'locality_id')
    create_dat_file(ind_by_locid, NUMBERS_LOCALITY_INDEX_PATH, 'int32')

    ind_by_geohs = index_list(NUMBER_DB_PATH, db.number_dtype, 'geohash')
    create_dat_file(ind_by_geohs, NUMBERS_GEOHASH_INDEX_PATH, 'int32')


def create_np_table(in_filename, dtype, out_filename, sort=None):
    nb_lines = utils.count_file_lines(in_filename)
    with open(in_filename, 'r+') as in_file,  \
            open(out_filename, 'wb+') as out_file:

        table = np.memmap(out_file, dtype=dtype, shape=(nb_lines,))

        for i, line in enumerate(in_file):
            table[i] = tuple(line.strip().split(';'))

        if sort:
            table.sort(order=sort)
            print('sorted %s on %s' % (out_filename, sort))

        table.flush()

    print_results(out_filename, table)

    return table


def print_results(filename, table):
    size = float(table.nbytes) / (1024 ** 2)
    print('written %s : %.3f MB' % (filename, size))


if __name__ == '__main__':
    print('INDEXING')

    if not os.path.exists(INDEX_PATH):
        os.mkdir(INDEX_PATH)

    create_info_tables()
    create_index_tables()

    print('DONE')
