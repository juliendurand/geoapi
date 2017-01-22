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

import itertools
import json
import os

import numpy as np
from unidecode import unidecode

import utils
import iris

SEPARATOR = ','

data_path = './data/ban'
index_path = './index/'
filename_template = 'BAN_licence_gratuite_repartage_%s.csv'

city_csv_path = 'index/cities.csv'
street_csv_path = 'index/streets.csv'
locality_csv_path = 'index/locality.csv'
number_csv_path = 'index/numbers.csv'

city_db_path = 'index/cities.dat'
street_db_path = 'index/streets.dat'
locality_db_path = 'index/localities.dat'
number_db_path = 'index/numbers.dat'
cities_post_index_path = 'index/cities_post_index.dat'
streets_insee_index_path = 'index/streets_insee_index.dat'
localities_insee_index_path = 'index/localities_insee_index.dat'
numbers_locality_index_path = 'index/numbers_locality_index.dat'
numbers_geohash_index_path = 'index/numbers_geohash_index.dat'

repetition_ref_path = 'index/repetitions.json'

departements = (
    '01', '02', '03', '04', '05', '06', '07', '08', '09', '10',
    '11', '12', '13', '14', '15', '16', '17', '18', '19', '21',
    '22', '23', '24', '25', '26', '27', '28', '29', '2A', '2B',
    '30', '31', '32', '33', '34', '35', '36', '37', '38', '39',
    '40', '41', '42', '43', '44', '45', '46', '47', '48', '49',
    '50', '51', '52', '53', '54', '55', '56', '57', '58', '59',
    '60', '61', '62', '63', '64', '65', '66', '67', '68', '69',
    '70', '71', '72', '73', '74', '75', '76', '77', '78', '79',
    '80', '81', '82', '83', '84', '85', '86', '87', '88', '89',
    '90', '91', '92', '93', '94', '95',
    '971', '972', '973', '974', '975', '976',
)

Address = (
    'id',
    'nom_voie',
    'id_fantoir',
    'numero',
    'rep',
    'code_insee',
    'code_post',
    'alias',
    'nom_ld',
    'nom_afnor',
    'libelle_acheminement',
    'x',
    'y',
    'lon',
    'lat',
    'nom_commune',
)

city_dtype = np.dtype([('code_insee', 'a5'),
                      ('code_post', 'a5'),
                      ('nom_commune', 'a45'),
                      ('lon', 'int32'),
                      ('lat', 'int32')])

street_dtype = np.dtype([('street_id', 'int32'),
                        ('code_insee', 'a5'),
                        ('code_post', 'a5'),
                        ('nom_voie', 'a32')])

# 'lieu-dit' in french
locality_dtype = np.dtype([('locality_id', 'int32'),
                          ('code_insee', 'a5'),
                          ('code_post', 'a5'),
                          ('nom_ld', 'a80')])

number_dtype = np.dtype([
    ('street_id', 'int32'),
    ('locality_id', 'int32'),
    ('number', 'int16'),
    ('rep', 'int8'),
    ('geohash', 'uint64'),
    ('code_iris', 'a9'),
])

#
# Index
#


def index_departement(departement, city_file, street_file, locality_file,
                      number_file, street_id_generator, locality_id_generator,
                      repetition_id_generator, repetitions):
    file = os.path.join(data_path, filename_template % departement)
    if not os.path.exists(file):
        print('ERROR for departement %s : file not found' % departement)
        return 1  # FIXME considered as skipping a line only

    print('Indexing : %s' % file)

    cities = {}
    streets = {}
    localities = {}
    numbers = set()

    with open(file, 'r', encoding='UTF-8') as in_file:
        next(in_file, None)  # skip header (first line)
        duplicates = 0
        nb_exceptions = 0
        for line in in_file:
            values = line[:-1].replace('""', '').split(';')
            try:
                numero = values[3]
                if int(numero) < 0:
                    raise Exception('Invalid numero : "%s"' % numero)

                rep = values[4]

                code_insee = values[5]
                if len(code_insee) != 5:
                    raise Exception('Invalid code_insee : "%s"' % code_insee)

                code_post = values[6]
                if len(code_post) != 5:
                    raise Exception('Invalid code_post : "%s"' % code_post)

                nom_ld = unidecode(values[8])
                if len(nom_ld) > 80:
                    raise Exception('Invalid nom_ld : "%s"' % nom_ld)

                nom_afnor = values[9]
                if len(nom_afnor) > 32:
                    raise Exception('Invalid nom_afnor : "%s"' % nom_afnor)

                nom_commune = values[10]
                if len(nom_commune) > 45:
                    raise Exception('Invalid nom_commune : "%s"' % nom_commune)

                x = float(values[11])

                y = float(values[12])

                lon = values[13]
                if not -180 <= float(lon) <= 180:
                    raise Exception('Invalid lon : "%s"' % lon)

                lat = values[14]
                if not -90 <= float(lat) <= 90:
                    raise Exception('Invalid lat : "%s"' % lat)

                city_key = hash(code_insee + ':' + code_post)
                if city_key not in cities:
                    cities[city_key] = {
                        'code_insee': code_insee,
                        'code_post': code_post,
                        'nom_commune': nom_commune,
                        'lon': [],
                        'lat': [],
                    }
                cities[city_key]['lon'].append(float(lon))
                cities[city_key]['lat'].append(float(lat))

                street_key = hash(code_insee + ':' + code_post + ':' +
                                  nom_afnor)
                if street_key not in streets:
                    street_id = str(next(street_id_generator))
                    streets[street_key] = street_id
                    street_line = ','.join((street_id, code_insee, code_post,
                                            nom_afnor,))
                    street_file.write(street_line + '\n')
                street_id = streets[street_key]

                locality_key = hash(code_insee + ':' + code_post + ':' +
                                    nom_ld)
                if locality_key not in localities:
                    locality_id = str(next(locality_id_generator))
                    localities[locality_key] = locality_id
                    locality_line = ','.join((locality_id, code_insee,
                                              code_post, nom_ld,))
                    locality_file.write(locality_line + '\n')
                locality_id = localities[locality_key]

                if rep not in repetitions:
                    repetition_key = str(next(repetition_id_generator))
                    repetitions[rep] = repetition_key
                rep = repetitions[rep]

                number_key = hash(street_id + ':' + locality_id + ':' +
                                  numero + ':' + rep)
                if number_key not in numbers:
                    numbers.add(number_key)
                    code_iris = iris.get_iris(code_insee, x, y)
                    number_line = ','.join((street_id, locality_id, numero,
                                            rep, lon, lat, code_iris))
                    number_file.write(number_line + '\n')
                else:
                    duplicates += 1
            except Exception as e:
                nb_exceptions += 1
                print(e)

        for city_key, city in cities.items():
            code_insee = city['code_insee']
            code_post = city['code_post']
            nom_commune = city['nom_commune']
            lon = np.mean(city['lon'])
            lat = np.mean(city['lat'])
            city_line = ','.join((code_insee, code_post, nom_commune, str(lon),
                                  str(lat)))
            city_file.write(city_line + '\n')
        if duplicates:
            print("duplicates: ", duplicates)
        if nb_exceptions:
            print("exceptions: ", nb_exceptions)
    return nb_exceptions


def process_csv_files():
    repetitions = {}
    nb_exceptions = 0
    street_id_generator = itertools.count()
    locality_id_generator = itertools.count()
    repetition_id_generator = itertools.count()

    with open(city_csv_path, 'w', encoding='UTF-8') as city_file, \
            open(street_csv_path, 'w', encoding='UTF-8') as street_file, \
            open(locality_csv_path, 'w', encoding='UTF-8') as locality_file, \
            open(number_csv_path, 'w', encoding='UTF-8') as number_file, \
            open(repetition_ref_path, 'w', encoding='UTF-8') as repetition_file:

        for departement in departements:
            nb_exceptions += index_departement(departement, city_file,
                                               street_file, locality_file,
                                               number_file,
                                               street_id_generator,
                                               locality_id_generator,
                                               repetition_id_generator,
                                               repetitions)

        print('TOTAL number of skipped lines : ', nb_exceptions)

        indexed_repetition = {int(v): k for k, v in repetitions.items()}
        indexed_repetition = sorted(indexed_repetition)
        repetition_file.write(json.dumps(indexed_repetition))
        print('saved repetition.json reference file')


def city_factory(line):
    code_insee, code_post, nom_commune, lon, lat = line[:-1].split(SEPARATOR)
    lon = utils.degree_to_int(float(lon))
    lat = utils.degree_to_int(float(lat))
    return (code_insee, code_post, nom_commune, lon, lat)


def street_factory(line):
    street_id, code_insee, code_post, nom_voie = line[:-1].split(SEPARATOR)
    street_id = int(street_id)
    return (street_id, code_insee, code_post, nom_voie,)


def locality_factory(line):
    locality_id, code_insee, code_post, nom_ld = line[:-1].split(SEPARATOR)
    locality_id = int(locality_id)
    return (locality_id, code_insee, code_post, nom_ld,)


def number_factory(line):
    street_id, locality_id, numero, rep, lon, lat, code_iris = \
        line[:-1].split(SEPARATOR)
    street_id = int(street_id)
    locality_id = int(locality_id)
    numero = utils.safe_cast(numero, int, -1)  # fixme
    if numero > 2**16 - 1:
        raise Exception('Error : numero overflows 16bits')
    return (street_id, locality_id, numero, rep,
            utils.geohash(float(lon), float(lat)), code_iris)


def create_np_table(in_filename, dtype, factory, out_filename, sort=None):
    nb_lines = utils.count_file_lines(in_filename)
    with open(in_filename, 'r+') as f, open(out_filename, 'wb+') as out_file:
        table = np.memmap(out_file, dtype=dtype, shape=(nb_lines,))
        for i, line in enumerate(f):
            table[i] = factory(line)
        if sort:
            table.sort(order=sort)
            print('sorted %s on %s' % (out_filename, sort))
        table.flush()
    print('written ', out_filename, ' : %.3f' % utils.b_to_mb(table.nbytes),
          'MB')
    os.remove(in_filename)
    return table


def create_np_index(table, column, out_filename):
    index_column = np.argsort(table, order=column).astype('int32')
    with open(out_filename, 'wb') as out_file:
        np.save(out_file, index_column)
    print('written ', out_filename, ' : %.3f' %
          utils.b_to_mb(index_column.nbytes),
          'MB')


def create_db():
    cities = create_np_table(city_csv_path, city_dtype, city_factory,
                             city_db_path, sort='code_insee')

    streets = create_np_table(street_csv_path, street_dtype, street_factory,
                              street_db_path)

    localities = create_np_table(locality_csv_path, locality_dtype,
                                 locality_factory, locality_db_path)

    numbers = create_np_table(number_csv_path, number_dtype, number_factory,
                              number_db_path, sort='street_id')

    create_np_index(cities, 'code_post', cities_post_index_path)
    create_np_index(streets, 'code_insee', streets_insee_index_path)
    create_np_index(localities, 'code_insee', localities_insee_index_path)
    create_np_index(numbers, 'locality_id', numbers_locality_index_path)
    create_np_index(numbers, 'geohash', numbers_geohash_index_path)


def load_data(file_path, dtype='int32'):
    return np.memmap(file_path, dtype=dtype)


def index():
    if not os.path.exists(index_path):
        os.mkdir(index_path)

    process_csv_files()
    create_db()


class AddressDatabase:

    def __init__(self):
        # data tables
        self.cities = load_data(city_db_path, dtype=city_dtype)
        self.streets = load_data(street_db_path, dtype=street_dtype)
        self.localities = load_data(locality_db_path, dtype=locality_dtype)
        self.numbers = load_data(number_db_path, dtype=number_dtype)

        # indices
        self.cities_post_index = load_data(cities_post_index_path)
        self.streets_insee_index = load_data(streets_insee_index_path)
        self.localities_insee_index = load_data(localities_insee_index_path)
        self.numbers_locality_index = load_data(numbers_locality_index_path)
        self.numbers_geohash_index = load_data(numbers_geohash_index_path)


if __name__ == '__main__':
    print('indexing')
    index()
