import itertools
import json
import os

from textprocessing import LineProcessor, FileProcessor

import references as ref
from update import UNZIP_PATH

DATA_PATH = UNZIP_PATH

CITY_CSV_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.CITY_CSV)
STREET_CSV_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.STREET_CSV)
LOCALITY_CSV_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.LOCALITY_CSV)
NUMBER_CSV_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.NUMBER_CSV)
REPETITION_JSON_PATH = os.path.join(ref.INTERMEDIATE_DIR, ref.REPETITION_JSON)


def process_departement(file_path, processed_file):
    print('Processing : %s' % file_path)

    exceptions = 0

    in_file = open(file_path, 'r', encoding='UTF-8')
    next(in_file, None)  # skip header (first line)

    for line in in_file:
        processed_line = LineProcessor(line)

        if not processed_line.test():
            exceptions += 1
            continue

        processed_file.update(processed_line)

    processed_file.finish(exceptions)


def process_csv_files():
    repetitions = dict()
    street_id_generator = itertools.count()
    locality_id_generator = itertools.count()
    repetition_id_generator = itertools.count()

    if not os.path.exists(ref.INTERMEDIATE_DIR):
        os.mkdir(ref.INTERMEDIATE_DIR)

    with open(CITY_CSV_PATH, 'w', encoding='UTF-8') as city_file, \
            open(STREET_CSV_PATH, 'w', encoding='UTF-8') as street_file, \
            open(LOCALITY_CSV_PATH, 'w', encoding='UTF-8') as locality_file, \
            open(NUMBER_CSV_PATH, 'w', encoding='UTF-8') as number_file, \
            open(REPETITION_JSON_PATH, 'w', encoding='UTF-8') as \
            repetition_file:

        for (dirname, dirs, files) in os.walk(DATA_PATH):
            for filename in files:
                if filename.endswith('.csv'):
                    file_path = os.path.join(dirname, filename)

                    processed_file = FileProcessor(city_file, street_file,
                                                   locality_file, number_file,
                                                   street_id_generator,
                                                   locality_id_generator,
                                                   repetition_id_generator,
                                                   repetitions)
                    process_departement(file_path, processed_file)

        indexed_repetition = {int(v[0]): k for k, v in repetitions.items()}
        indexed_repetition = sorted(indexed_repetition)
        repetition_file.write(json.dumps(indexed_repetition))
        print('saved repetition.json reference file')


if __name__ == '__main__':
    print('CREATING INTERMEDIATE CSV DATABASE')

    process_csv_files()

    print("DONE")
