import bisect
import difflib
import json
import re


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


def find(x, index, values):
    lo = 0
    hi = len(index)
    while lo < hi:
        mid = (lo+hi)//2
        midval = values[index[mid]]
        if midval < x:
            lo = mid+1
        elif midval > x:
            hi = mid
        else:
            return mid
    return -1


def search(db, code_insee, query):
    query = query.lower()
    number = get_number(query)
    match = None
    max_score = 0
    street_idx = find(code_insee, db.code_insee_index, db.streets)
    while True:
        street_id = db.code_insee_index[street_idx]
        street = db.streets[street_id]
        if street['code_insee'] != code_insee:
            break
        score = score_street(query, street['nom_voie'])
        if score > max_score:
            max_score = score
            match = street
        street_idx += 1
    street_id = match['street_id']
    number_match = None
    # for numero in match['numeros']:
    #    if numero['numero'] == str(number):
    #        number_match = numero
    return {
        'code_insee': code_insee,
        'nom_voie': match['nom_voie'],
        # 'numero': number,
        # 'lat': number_match['lat'] if number_match else "",
        # 'lon': number_match['lon'] if number_match else "",
        }
