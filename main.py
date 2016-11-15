from collections import namedtuple

import csv
import difflib
import json
import os
import re

data_path = './data/ban'
index_path = './index/'
filename_template = 'BAN_licence_gratuite_repartage_%s.csv'

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

db = {}


def index_departement(departement):
    file = os.path.join(data_path, filename_template % departement)
    if not os.path.exists(file):
        print('ERROR for departement %s : file not found' % departement)
        return
    print('Indexing : %s' % file)
    csv_reader = csv.reader(open(file, 'r'), delimiter=';')
    next(csv_reader, None)
    for address in map(Address._make, csv_reader):
        code_insee = address.code_insee
        code_post = address.code_post
        nom_commune = address.nom_commune
        if not db.get(code_insee):
            db[code_insee] = City(code_insee, code_post, nom_commune, {})
        city = db[code_insee]
        streets = city.streets

        nom_voie = address.nom_voie
        if not streets.get(nom_voie):
            streets[nom_voie] = Street(nom_voie, {})
        street = streets[nom_voie]
        numbers = street.numbers

        numero = address.numero
        rep = address.rep
        lon = address.lon
        lat = address.lat
        if not numbers.get(numero+rep):
            numbers[numero+rep] = Number(numero, rep, lon, lat)


def save_db():
    for code_insee in db:
        city = db[code_insee]
        out_filename = get_code_insee_filename(code_insee)
        with open(out_filename, 'w') as out:
            for street in city.streets:

                out.write(street_to_json(city.streets[street]) + '\n')
    db = {}


def index():
    for departement in departements:
        index_departement(departement)
        # save_db()


def score_street(query, street):
    intersection = set(query.lower().split()) & \
        set(street['nom'].lower().split())
    return len(intersection)
    #return difflib.SequenceMatcher(a=query.lower(),
    #                               b=street['nom'].lower()).ratio()


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


index()

# result = get('44109', '40, chemin de la conardière')
# print (result)
