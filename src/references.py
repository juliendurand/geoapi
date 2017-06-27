# -*- coding: utf-8 -*-
"""Main directory references as attributes and statement.

This module has all the the useful directory names and paths as attributes
and/or statements. It serves as a easy way to reference the directories
involved with the data manipulation.

Attributes:
    DATA_DIR (str): The name of the directory where the zip file containing the
        BASE ADRESSE NATIONALE (BAN) will be downloaded.
    BAN_SUBDIR (str): The name of the directory where the downloaded zip file
        will be uncompressed.
    INTERMEDIATE_DIR (str): The name of the directory where the intermediary
        csv database will be built.
    INDEX_DIR (str): The name of the directory where the '.dat' database will
        be finally built.

    URL (str): The location of the BASE ADRESSE NATIONALE (BAN) compressed in
        zip format.

    CITY_CSV = Name of the new csv file containig the information about the
        cities (communes) in France.
    STREET_CSV = Name of the new csv file containing information about the
        routes in France.
    LOCALITY_CSV = Name of the new csv file containing information about the
        localities (lieu-dit) in France.
    NUMBER_CSV = Name of the new csv file containig information about
        the numbers in France.
    REPETITION_JSON = Name of the new json file containing the mapping between
        integers and 'repetition' strings (the french complement to addresses
        numbers).

    CITY_DB (str): The name of the '.dat' file where the information about the
        cities will be written.
    STREET_DB (str): The name of the '.dat' file where the information about
        the streets will be written.
    LOCALITY_DB (str): The name of the '.dat' file where the information about
        the localities will be written.
    NUMBER_DB (str): The path of the '.dat' file where the information about
        the numbers will be written.

    CITIES_POST_INDEX (str): The name of the '.dat' file where the indices
        of the cities table, after sorting it by zip code (code postal), will
        be written.
    STREETS_INSEE_INDEX (str): The name of the '.dat' file where the
        indices of the streets table, after sorting it by code insee, will be
        written.
    LOCALITIES_INSEE_INDEX (str): The name of the '.dat' file where the
        indices of the localities table, after sorting it by code insee, will
        be written.
    NUMBERS_LOCALITY_INDEX (str): The name of the '.dat' file where the
        indices of the numbers table, after sorting it by locality_id, will
        be written.
    NUMBERS_GEOHASH_INDEX (str): The name of the '.dat' file where the
        indices of the numbers table, after sorting it by geohash, will
        be written.

"""

import os

DATA_DIR = 'data'
BAN_SUBDIR = 'ban'
INTERMEDIATE_DIR = 'database_csv'
INDEX_DIR = 'database_dat'

URL = 'https://adresse.data.gouv.fr/data/BAN_licence_gratuite_repartage.zip'

FILE = 'ban.zip'

FILE_PATH = os.path.join(DATA_DIR, FILE)
UNZIP_PATH = os.path.join(DATA_DIR, BAN_SUBDIR)

CITY_CSV = 'cities.csv'
STREET_CSV = 'streets.csv'
LOCALITY_CSV = 'locality.csv'
NUMBER_CSV = 'numbers.csv'
REPETITION_JSON = 'repetitions.json'

CITY_DB = 'cities.dat'
STREET_DB = 'streets.dat'
LOCALITY_DB = 'localities.dat'
NUMBER_DB = 'number.dat'

CITIES_POST_INDEX = 'cities_post_index.dat'
STREETS_INSEE_INDEX = 'streets_insee_index.dat'
LOCALITIES_INSEE_INDEX = 'localities_insee_index.dat'
NUMBERS_LOCALITY_INDEX = 'numbers_locality_index.dat'
NUMBERS_GEOHASH_INDEX = 'numbers_geohash_index.dat'

CITY_CSV_PATH = os.path.join(INTERMEDIATE_DIR, CITY_CSV)
STREET_CSV_PATH = os.path.join(INTERMEDIATE_DIR, STREET_CSV)
LOCALITY_CSV_PATH = os.path.join(INTERMEDIATE_DIR, LOCALITY_CSV)
NUMBER_CSV_PATH = os.path.join(INTERMEDIATE_DIR, NUMBER_CSV)
REPETITION_JSON_PATH = os.path.join(INTERMEDIATE_DIR, REPETITION_JSON)

CITY_DB_PATH = os.path.join(INDEX_DIR, CITY_DB)
STREET_DB_PATH = os.path.join(INDEX_DIR, STREET_DB)
LOCALITY_DB_PATH = os.path.join(INDEX_DIR, LOCALITY_DB)
NUMBER_DB_PATH = os.path.join(INDEX_DIR, NUMBER_DB)

CITIES_POST_INDEX_PATH = os.path.join(INDEX_DIR, CITIES_POST_INDEX)
STREETS_INSEE_INDEX_PATH = os.path.join(INDEX_DIR, STREETS_INSEE_INDEX)
LOCALITIES_INSEE_INDEX_PATH = os.path.join(INDEX_DIR, LOCALITIES_INSEE_INDEX)
NUMBERS_LOCALITY_INDEX_PATH = os.path.join(INDEX_DIR, NUMBERS_LOCALITY_INDEX)
NUMBERS_GEOHASH_INDEX_PATH = os.path.join(INDEX_DIR, NUMBERS_GEOHASH_INDEX)
