import itertools
import json
import os

import numpy as np

import reverse
import utils

SEPARATOR = ','

data_path = './data/ban'
index_path = './index/'
filename_template = 'BAN_licence_gratuite_repartage_%s.csv'

city_csv_path = 'index/cities.csv'
street_csv_path = 'index/streets.csv'
number_csv_path = 'index/numbers.csv'

city_db_path = 'index/cities.dat'
street_db_path = 'index/streets.dat'
number_db_path = 'index/numbers.dat'

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
                      ('nom_commune', 'a45')])

street_dtype = np.dtype([('street_id', 'int32'),
                        ('code_insee', 'a5'),
                        ('nom_voie', 'a32')])

location_dtype = np.dtype([('lon', 'int32'),
                           ('lat', 'int32')])

number_dtype = np.dtype([('street_id', 'int32'),
                        ('number', 'int16'),
                        ('rep', 'int8'),
                        ('location', location_dtype)])

#
# Index
#


def index_departement(departement, city_file, street_file, number_file,
                      street_id_generator, repetition_id_generator,
                      repetitions):
    file = os.path.join(data_path, filename_template % departement)
    if not os.path.exists(file):
        print('ERROR for departement %s : file not found' % departement)
        return 1  # FIXME considered as skipping a line only

    print('Indexing : %s' % file)

    cities = set()
    streets = {}
    numbers = set()

    with open(file, 'r') as in_file:
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
                if len(code_insee) > 5:
                    raise Exception('Invalid code_insee : "%s"' % code_insee)

                code_post = values[6]
                if len(code_post) > 5:
                    raise Exception('Invalid code_post : "%s"' % code_post)

                nom_afnor = values[9]
                if len(code_post) > 32:
                    raise Exception('Invalid nom_afnor : "%s"' % code_post)

                nom_commune = values[10]
                if len(code_post) > 45:
                    raise Exception('Invalid nom_commune : "%s"' % nom_commune)

                lon = values[13]
                if not -180 < float(lon) < 180:
                    raise Exception('Invalid lon : "%s"' % lon)

                lat = values[14]
                if not -90 < float(lat) < 90:
                    raise Exception('Invalid lat : "%s"' % lat)

                if code_insee not in cities:
                    cities.add(code_insee)
                    city_line = ','.join((code_insee, code_post, nom_commune,))
                    city_file.write(city_line + '\n')

                street_key = hash(code_insee + ':' + nom_afnor)
                if street_key not in streets:
                    street_id = str(next(street_id_generator))
                    streets[street_key] = street_id
                    street_line = ','.join((street_id, code_insee, nom_afnor,))
                    street_file.write(street_line + '\n')
                street_id = streets[street_key]

                number_key = hash(street_id + ':' + numero + ':' + rep)
                if number_key not in numbers:
                    if rep not in repetitions:
                        repetition_key = str(next(repetition_id_generator))
                        repetitions[rep] = repetition_key
                    rep = repetitions[rep]
                    numbers.add(number_key)
                    number_line = ','.join((street_id, numero, rep, lon, lat,))
                    number_file.write(number_line + '\n')
                else:
                    duplicates += 1
            except Exception as e:
                nb_exceptions += 1
                print(e)
        if duplicates:
            print("duplicates: ", duplicates)
        if nb_exceptions:
            print("exceptions: ", nb_exceptions)
    return nb_exceptions


def city_factory(line):
    code_insee, code_post, nom_commune = line[:-1].split(SEPARATOR)
    return (code_insee, code_post, nom_commune,)


def street_factory(line):
    street_id, code_insee, nom_voie = line[:-1].split(SEPARATOR)
    street_id = int(street_id)
    return (street_id, code_insee, nom_voie,)


def number_factory(line):
    street_id, numero, rep, lon, lat = line[:-1].split(SEPARATOR)
    street_id = int(street_id)
    numero = utils.safe_cast(numero, int, -1)  # fixme
    if numero > 2**16 - 1:
        raise Exception('Error : numero overflows 16bits')
    lon = utils.degree_to_int(float(lon))
    lat = utils.degree_to_int(float(lat))
    return (street_id, numero, rep, (float(lon), float(lat),),)


def create_np_table(in_filename, dtype, factory, out_filename, sort=None):
    nb_lines = utils.count_file_lines(in_filename)
    table = np.memmap(out_filename, dtype=dtype, mode="w+", shape=(nb_lines,))
    with open(in_filename, "r+") as f:
        for i, line in enumerate(f):
            table[i] = factory(line)
    if sort:
        table.sort(order=sort)
        print('sorted %s on %s' % (out_filename, sort))
    table.flush()
    print('written ', out_filename, ' : %.3f' % utils.b_to_mb(table.nbytes),
          'MB')
    #os.remove(in_filename) TODO remove
    return table


def create_db():
    create_np_table(city_csv_path, city_dtype, city_factory,
                    city_db_path, sort='code_insee')

    create_np_table(street_csv_path, street_dtype, street_factory,
                    street_db_path)

    create_np_table(number_csv_path, number_dtype, number_factory,
                    number_db_path, sort='street_id')


def index():
    if not os.path.exists('index'):
        os.mkdir('index')

    repetitions = {}
    nb_exceptions = 0
    street_id_generator = itertools.count()
    repetition_id_generator = itertools.count()

    with open(city_csv_path, 'w') as city_file, \
            open(street_csv_path, 'w') as street_file, \
            open(number_csv_path, 'w') as number_file, \
            open(repetition_ref_path, 'w') as repetition_file:

        for departement in departements:
            nb_exceptions += index_departement(departement, city_file,
                                               street_file, number_file,
                                               street_id_generator,
                                               repetition_id_generator,
                                               repetitions)

        print('TOTAL number of skipped lines : ', nb_exceptions)

        indexed_repetition = {int(v): k for k, v in repetitions.items()}
        indexed_repetition = sorted(indexed_repetition)
        repetition_file.write(json.dumps(indexed_repetition))
        print('saved repetition.json reference file')

        create_db()


#
# Load
#


def load_db():
    cities = np.memmap(city_db_path, dtype=city_dtype, mode='r')
    streets = np.memmap(street_db_path, dtype=street_dtype, mode='r')
    numbers = np.memmap(number_db_path, dtype=number_dtype, mode='r')
    return {
        'cities': cities,
        'streets': streets,
        'numbers': numbers,
        'insee_index': np.argsort(streets, order='code_insee')
    }


if __name__ == '__main__':
    #index()
    #create_db()
    db = load_db()
    import time

    start = time.time()
    kd_tree = reverse.kd_tree_index(db)
    end = time.time()
    print("kd-tree indexing ", (end-start))

    start = time.time()
    #reverse.reverse(kd_tree, db, 2.156033, 48.93589)
    reverse.reverse(kd_tree, db, 3.109815, 47.239012)
    end = time.time()
    print("kdtree ", (end-start))
