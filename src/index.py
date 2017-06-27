# -*- coding: utf-8 -*-
"""Creation of the final database in dat format.

This module creates the final database, stored in binary files with the
extension '.dat'. Each file of the database represents a numpy array and they
are divided in two types: the information tables and the index tables. The
information tables store the real data about the addresses while index tables
just store the order in which the elements of the information tables would
appear for a given sort.

"""

import os
import numpy as np

import datatypes as dtp
import references as ref

INDEX_PATH = ref.INDEX_DIR

CITY_CSV_PATH = ref.CITY_CSV_PATH
STREET_CSV_PATH = ref.STREET_CSV_PATH
LOCALITY_CSV_PATH = ref.LOCALITY_CSV_PATH
NUMBER_CSV_PATH = ref.NUMBER_CSV_PATH

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


def create_dat_file(lst, out_filename, dtype):
    """Write a list in a binary file as a numpy array.

    Args:
        lst: The list that will be written in the file.
        out_filename: The name of the binary file. It must be in the same
            directory.
        dtype: The type of the numpy array.

    """
    with open(out_filename, 'wb+') as out_file:
        dat_file = np.memmap(out_file, dtype=dtype, shape=(len(lst),))
        dat_file[:] = lst[:]
        dat_file.flush()
    print_results(out_filename, dat_file)


def sort_table(in_filename, dtype, field):
    """Sort a numpy array stored in a file following a certain criteria.

    This method sorts a numpy array of objects stored in a binary file using a
    field of the object as the value to compare.

    Args:
        in_filename (str): The name of the file where the array is stored.
        dtype (np.dtype): The type of the objects in the array.
        field (str): The name of the field of the object to be used in the
            comparisons.

    """
    table = np.memmap(in_filename, dtype=dtype)
    table.sort(order=field)
    table.flush()

    print('sorted %s on %s' % (in_filename, field))


def csv_to_list(in_filename):
    in_file = open(in_filename, 'r+')
    return [tuple(line.strip().split(';')) for line in in_file]


def index_list(in_filename, dtype, column):
    """Return the indices of a sorted numpy array stored in a file.

    This method sorts a numpy array of objects stored in a binary file using a
    field of the object as the value to compare and returns the indices of this
    new array.

    Args:
        in_filename (str): The name of the file where the array is stored.
        dtype (np.dtype): The type of the objects in the array.
        field (str): The name of the field of the object to be used in the
            comparisons.

    Returns:
        list: The list of indices (int list).

    """
    table = np.memmap(in_filename, dtype=dtype)
    indexes_list = np.argsort(table, order=column).astype('int32')
    return indexes_list


def create_info_tables():
    city_list = csv_to_list(CITY_CSV_PATH)
    create_dat_file(city_list, CITY_DB_PATH, city_dtype)

    street_list = csv_to_list(STREET_CSV_PATH)
    create_dat_file(street_list, STREET_DB_PATH, street_dtype)

    locality_list = csv_to_list(LOCALITY_CSV_PATH)
    create_dat_file(locality_list, LOCALITY_DB_PATH, locality_dtype)

    number_list = csv_to_list(NUMBER_CSV_PATH)
    create_dat_file(number_list, NUMBER_DB_PATH, number_dtype)

    # Sort tables
    sort_table(CITY_DB_PATH, city_dtype, 'code_insee')
    sort_table(NUMBER_DB_PATH, number_dtype, 'street_id')


def create_index_tables():
    ind_by_post = index_list(CITY_DB_PATH, city_dtype, 'code_post')
    create_dat_file(ind_by_post, CITIES_POST_INDEX_PATH, 'int32')

    st_ind_by_insee = index_list(STREET_DB_PATH, street_dtype, 'code_insee')
    create_dat_file(st_ind_by_insee, STREETS_INSEE_INDEX_PATH, 'int32')

    loc_ind_by_insee = index_list(LOCALITY_DB_PATH, locality_dtype,
                                  'code_insee')
    create_dat_file(loc_ind_by_insee, LOCALITIES_INSEE_INDEX_PATH, 'int32')

    ind_by_locid = index_list(NUMBER_DB_PATH, number_dtype, 'locality_id')
    create_dat_file(ind_by_locid, NUMBERS_LOCALITY_INDEX_PATH, 'int32')

    ind_by_geohs = index_list(NUMBER_DB_PATH, number_dtype, 'geohash')
    create_dat_file(ind_by_geohs, NUMBERS_GEOHASH_INDEX_PATH, 'int32')


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
