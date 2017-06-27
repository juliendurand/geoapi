# -*- coding: utf-8 -*-
"""Creation of an intermediary database in csv format.

This module creates an intermediary database in csv format. The goal of this
intermediate step is to easy the next step: the construction of the binary
files using tools from the package numpy.

The treatment of all the input and output data is described at the
textprocessing module.

Attributes:
    DATA_PATH (str): Path to the csv files containing the information of each
        departement.
    CITY_CSV_PATH (str): Path to the new csv file containig the information
        about the cities (communes) in France.
    STREET_CSV_PATH (str): Path to the new csv file containing information
        about the routes in France.
    LOCALITY_CSV_PATH  (str): Path to the new csv file containing information
        about the localities (lieu-dit) in France.
    NUMBER_CSV_PATH (str): Path to the new csv file containig information about
        the localities in France.
    REPETITION_JSON_PATH (str): Path to the new json file containing the
        mapping between integers and 'repetition' strings (the french
        complement to addresses numbers).

Todo:
    * Transfer the processing of the repetitions file to the textprocessing
    module

"""

import json
import os

from textprocessing import FileProcessor

import references as ref
from update import UNZIP_PATH

DATA_PATH = UNZIP_PATH

CITY_CSV_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.CITY_CSV)
STREET_CSV_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.STREET_CSV)
LOCALITY_CSV_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.LOCALITY_CSV)
NUMBER_CSV_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.NUMBER_CSV)
REPETITION_JSON_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.REPETITION_JSON)


def process_csv_files():
    """Manage the process of all the csv files and the writing of the new ones.

    This method opens the csv files where the intermediary database will be
    written and menages the processing of each file which is done by an
    instance of FileProcessor from the module textprocessing.

    """

    if not os.path.exists(ref.INTERMEDIATE_DIR):
        os.mkdir(ref.INTERMEDIATE_DIR)

    with open(CITY_CSV_PATH, 'w', encoding='UTF-8') as city_file, \
            open(STREET_CSV_PATH, 'w', encoding='UTF-8') as street_file, \
            open(LOCALITY_CSV_PATH, 'w', encoding='UTF-8') as locality_file, \
            open(NUMBER_CSV_PATH, 'w', encoding='UTF-8') as number_file, \
            open(REPETITION_JSON_PATH, 'w', encoding='UTF-8') as \
            repetition_file:

        fileProc = FileProcessor(city_file, street_file, locality_file,
                                 number_file)

        for (dirname, dirs, files) in os.walk(DATA_PATH):
            for filename in files:
                if filename.endswith('.csv'):
                    file_path = os.path.join(dirname, filename)

                    print('Processing : %s' % file_path)

                    in_file = open(file_path, 'r', encoding='UTF-8')
                    fileProc.process(in_file)

        repetitions = fileProc.repetitions
        indexed_repetition = {int(v[0]): k for k, v in repetitions.items()}
        indexed_repetition = sorted(indexed_repetition)
        repetition_file.write(json.dumps(indexed_repetition))
        print('saved repetition.json reference file')


if __name__ == '__main__':
    print('CREATING INTERMEDIATE CSV DATABASE')

    process_csv_files()

    print("DONE")
