# -*- coding: utf-8 -*-
"""Creation of an intermediary database in csv format.

This module creates an intermediary database in csv format. The goal of this
intermediate step is to easy the next step: the construction of the binary
files using tools from the package numpy.

The treatment of all the input and output data is described at the
textprocessing module.

Todo:
    * Transfer the processing of the repetitions file to the textprocessing
    module.

"""

import json
import os

from textprocessing import FileProcessor

import references as ref

DATA_PATH = ref.UNZIP_PATH

CITY_CSV_PATH = ref.CITY_CSV_PATH
STREET_CSV_PATH = ref.STREET_CSV_PATH
LOCALITY_CSV_PATH = ref.LOCALITY_CSV_PATH
NUMBER_CSV_PATH = ref.NUMBER_CSV_PATH
REPETITION_JSON_PATH = ref.REPETITION_JSON_PATH


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
    print('CREATING INTERMEDIARY CSV DATABASE')

    process_csv_files()

    print("DONE")
