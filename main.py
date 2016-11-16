from collections import namedtuple

import difflib
import itertools
import json
import mmap
import os
import re

import numpy as np

SEPARATOR = ','
DEGREE_TO_INT_SCALE = 10000000

data_path = './data/ban'
index_path = './index/'
filename_template = 'BAN_licence_gratuite_repartage_%s.csv'

city_db_path = 'index/cities.csv'
street_db_path = 'index/streets.csv'
number_db_path = 'index/numbers.csv'

# bug : missing departement 62
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

Address = namedtuple("Address", (
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
)

City = namedtuple('City', ('code_insee', 'code_post', 'nom_commune',
                           'streets', ))
Street = namedtuple('Street', ('nom_voie', 'numbers', ))
Number = namedtuple('Number', ('numero', 'rep', 'lon', 'lat', ))


city_dtype = np.dtype([('code_insee', 'a5'),
                      ('code_post', 'a5'),
                      ('nom_commune', 'a45')])

street_dtype = np.dtype([('street_id', 'a5'),
                        ('code_insee', 'a5'),
                        ('nom_voie', 'a32')])

number_dtype = np.dtype([('street_id', 'a5'),
                        ('number', 'int16'),
                        ('rep', 'a3'),
                        ('lon', 'int32'),
                        ('lat', 'int32')])


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default or to_type()


def degree_to_int(angle):
    return int(angle*DEGREE_TO_INT_SCALE) if -180 < angle < 180 else 0  # FIXME


def int_to_degree(value):
    return float(value)/DEGREE_TO_INT_SCALE


def b_to_mb(bytes):
    return float(bytes)/1024**2


def get_code_insee_filename(code_insee):
    root = code_insee[:2]
    folder = os.path.join(index_path, root)
    if not os.path.exists(folder):
        os.mkdir(folder)
    return os.path.join(folder, code_insee+'.json')


def street_to_json(street):
    data = {
        'nom': street.nom_voie,
        'numeros': [v._asdict() for k, v in street.numbers.items()]
    }
    return json.dumps(data)

street_id_generator = itertools.count()


def index_departement(departement, city_file, street_file, number_file):
    file = os.path.join(data_path, filename_template % departement)
    if not os.path.exists(file):
        print('ERROR for departement %s : file not found' % departement)
        return
    print('Indexing : %s' % file)
    cities = set()
    streets = {}
    numbers = set()
    duplicates = 0
    with open(file, 'r') as in_file:
        next(in_file, None)  # skip header (first line)
        for line in in_file:
            values = line[:-1].replace('""', '').split(';')

            numero = values[3]
            rep = values[4]
            code_insee = values[5]
            code_post = values[6]
            nom_afnor = values[9]
            nom_commune = values[10]
            lon = values[13]
            lat = values[14]

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
                numbers.add(number_key)
                try:
                    nb = int(numero)
                    l = float(lon)
                    ll = float(lat)
                except:
                    print(numero, lon, lat)
                number_line = ','.join((street_id, numero, rep, lon, lat,))
                number_file.write(number_line + '\n')
            else:
                duplicates += 1
                #print("Duplicate number : should not happen !")
        print("streets", len(streets))
        print("duplicates", duplicates)


def count_file_lines(filename):
    lines = 0
    with open(filename, "r+") as f:
        buf = mmap.mmap(f.fileno(), 0)
        readline = buf.readline
        while readline():
            lines += 1
    return lines


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
    numero = safe_cast(numero, int, -1)  # fixme
    if numero > 2**16 - 1:
        raise "Error : numero overflows 16bits"
    lon = degree_to_int(float(lon))
    lat = degree_to_int(float(lat))
    return (street_id, numero, rep, lon, lat,)


def create_np_table(filename, dtype, factory):
    nb_lines = count_file_lines(filename)
    table = np.zeros(nb_lines, dtype=dtype)
    with open(filename, "r+") as f:
        i = 0
        for line in f:
            table[i] = factory(line)
            i += 1
    return table


def index():
    with open(city_db_path, 'w') as city_file, \
            open(street_db_path, 'w') as street_file, \
            open(number_db_path, 'w') as number_file:
        for departement in departements:
            index_departement(departement, city_file, street_file, number_file)


def score_street(query, street):
    intersection = set(query.lower().split()) & \
        set(street['nom'].lower().split())
    return len(intersection)
    #return difflib.SequenceMatcher(a=query.lower(),
    #                               b=street['nom'].lower()).   ratio()


def get_number(query):
    for token in re.findall(r'\d+', query):
        try:
            number = int(token)
            return number
        except:
            pass
    return 0

import time


def get(code_insee, query):
    query = query.lower()
    number = get_number(query)
    match = None
    start = time.perf_counter()
    with open(get_code_insee_filename(code_insee), 'r') as db:
        max_score = 0
        for line in db:
            street = json.loads(line)
            score = score_street(query, street)
            if score > max_score:
                max_score = score
                match = street
    number_match = None
    stop = time.perf_counter()
    print (stop-start)
    for numero in match['numeros']:
        if numero['numero'] == str(number):
            number_match = numero
    return {
        'code_insee': code_insee,
        'voie': match['nom'],
        'numero': number,
        'lat': number_match['lat'] if number_match else "",
        'lon': number_match['lon'] if number_match else "",
        }

#print(count_file_lines(city_db_path))
#print(count_file_lines(street_db_path))
#print(count_file_lines(number_db_path))

#index(); exit()

#with open('index/cities.csv', encoding='utf-8') as fp:
#    cities = np.loadtxt(fp, dtype=[('code_insee', 'str_'), ('code_post', 'str_'), ('nom_commune', 'str_')], delimiter=',')

#with open('index/numbers.csv') as fp:
#    maxlen = 0
#    maxnb = 0
#    repset = set()
#    for line in fp:
#        values = line[:-1].split(',')
#        maxnb = max(maxnb, len(values[1]))
#        maxlen = max(maxlen, len(values[2]))
#        repset.add(values[2].upper())
#
#    print("maxrep: ", maxlen, " max number: ", maxnb)
#    print(repset, len(repset))

#
# max city name length = 45 unicode /!\ utf-8
#


def load_db():
    cities = create_np_table(city_db_path, city_dtype, city_factory)
    print('cities: ', '%.3f' % b_to_mb(cities.nbytes), 'MB')

    streets = create_np_table(street_db_path, street_dtype, street_factory)
    print('streets: ', '%.3f' % b_to_mb(streets.nbytes), 'MB')

    numbers = create_np_table(number_db_path, number_dtype, number_factory)
    print('numbers: ', '%.3f' % b_to_mb(numbers.nbytes), 'MB')

    return {
        'cities': cities,
        'streets': streets,
        'numbers': numbers
    }

print('main.py reloaded')

if __name__ == '__main__':
    db = load_db()
    db['streets'].sort(order='code_insee')
    print('sorted streets')

    db['numbers'].sort(order='street_id')
    print('sorted numbers')
