import difflib
import json
import re


def street_to_json(street):
    data = {
        'nom': street.nom_voie,
        'numeros': [v._asdict() for k, v in street.numbers.items()]
    }
    return json.dumps(data)


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


def search(db, code_insee, query):
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
