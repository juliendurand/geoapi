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


def create_np_table(in_filename, dtype, out_filename, sort=None):
    nb_lines = utils.count_file_lines(in_filename)
    with open(in_filename, 'r+') as f, open(out_filename, 'wb+') as out_file:

        table = np.memmap(out_file, dtype=dtype, shape=(nb_lines,))

        for i, line in enumerate(f):
            try:
                table[i] = tuple(line.strip().split(';'))
            except ValueError:
                print(line)

        if sort:
            table.sort(order=sort)
            print('sorted %s on %s' % (out_filename, sort))

        table.flush()

    print_results(out_filename, table)

    return table


def create_np_index(table, column, out_filename):
    index_column = np.argsort(table, order=column).astype('int32')

    with open(out_filename, 'wb') as out_file:
        np.save(out_file, index_column)

    print_results(out_filename, table)


def print_results(filename, table):
    size = float(table.nbytes) / (1024 ** 2)
    print('written %s : %.3f MB' % (filename, size))


def create_db():
    cities = create_np_table(CITY_CSV_PATH, db.city_dtype, db.CITY_DB_PATH,
                             sort='code_insee')
    streets = create_np_table(STREET_CSV_PATH, db.street_dtype,
                              db.STREET_DB_PATH)
    localities = create_np_table(LOCALITY_CSV_PATH, db.locality_dtype,
                                 db.LOCALITIES_DB_PATH)
    numbers = create_np_table(NUMBER_CSV_PATH, db.number_dtype,
                              db.NUMBER_DB_PATH, sort='street_id')

    create_np_index(cities, 'code_post', db.CITIES_POST_INDEX_PATH)
    create_np_index(streets, 'code_insee', db.STREETS_INSEE_INDEX_PATH)
    create_np_index(localities, 'code_insee', db.LOCALITIES_INSEE_INDEX_PATH)
    create_np_index(numbers, 'locality_id', db.NUMBERS_LOCALITY_INDEX_PATH)
    create_np_index(numbers, 'geohash', db.NUMBERS_GEOHASH_INDEX_PATH)


if __name__ == '__main__':
    print('INDEXING')

    if not os.path.exists(INDEX_PATH):
        os.mkdir(INDEX_PATH)

    create_db()

    print('DONE')
