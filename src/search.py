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


import re
from itertools import chain
import time

from unidecode import unidecode

from address import Result
from trigram import Trigram
from utils import reverse_geohash, find, find_index, find_all_from_index


def best_match(query, items, min_score=0.5):
    match = None
    max_score = 0
    if query:
        t = Trigram(query)
        for i, item in enumerate(items):
            score = t.score(item) if item else 0
            if score == 1.0:
                return (i, 1.0,)
            if score > max_score and score > min_score:
                match = i
                max_score = score
    return (match, max_score,)


def clean_query(query):
    query = query.replace(' BD ', ' BOULEVARD ')
    query = query.replace(' AV ', ' AVENUE ')
    return query


def get_number(query):
    number = 0
    for token in re.findall(r'(^|\W)(\d+)', query):
        try:
            number = int(token[1])
        except:
            pass
    return number


def get_repetition(query):
    # TODO
    pass


def search_insee(db, code_post, city):
    city = city.replace('CEDEX', '')
    city_pos_list = find_all_from_index(code_post, db.cities_post_index,
                                        db.cities['code_post'], string=True)
    cities = [db.cities[pos] for pos in city_pos_list]
    if len(cities) == 0:
        lo = find_index(code_post[:2] + '000', db.cities_post_index,
                        db.cities['code_post'], string=True)
        hi = find_index(code_post[:2] + '999', db.cities_post_index,
                        db.cities['code_post'], string=True)
        cities = [db.cities[db.cities_post_index[idx]] for idx
                  in range(lo, hi + 1)]
    names = [c['nom_commune'].decode('UTF-8') for c in cities]
    city, max_score = best_match(city, names)
    return cities[city]['code_insee'].decode('UTF-8') if city is not None \
        else None


def search_street(db, code_insee_list, code_post, query):
    # find street
    min_score = 0.5
    street_pos_list = []
    for code in code_insee_list:
        street_pos_list.append(find_all_from_index(code,
                                                   db.streets_insee_index,
                                                   db.streets['code_insee'],
                                                   string=True))
    street_pos_list = chain(*street_pos_list)
    streets = [db.streets[pos] for pos in street_pos_list]
    names = [s['nom_voie'].decode('UTF-8') for s in streets]
    street, max_score = best_match(query, names, min_score=min_score)
    match_id = streets[street]['street_id'] if street is not None else None
    return (match_id, max_score,)


def search_locality(db, code_insee_list, query, min_score):
    # find locality
    min_score = max(0.7, min_score)
    locality_pos_list = []
    for code in code_insee_list:
        locality_pos_list.append(
            find_all_from_index(code, db.localities_insee_index,
                                db.localities['code_insee'], string=True)
        )
    locality_pos_list = chain(*locality_pos_list)
    localities = [db.localities[pos] for pos in locality_pos_list]
    names = [l['nom_ld'].decode('UTF-8') for l in localities]
    locality, max_score = best_match(query, names, min_score=min_score)
    match_id = localities[locality]['locality_id'] if locality is not None \
        else None

    return (match_id, max_score,)


def search_number(db, street_id, locality_id, number, max_score):
    if locality_id:
        result_idx = find_index(locality_id, db.numbers_locality_index,
                                db.numbers['locality_id'])
        n_idx = db.numbers_locality_index[result_idx]
        return Result.from_plate(db, n_idx, max_score)
    elif number:
        n_idx = find(street_id, db.numbers['street_id'])
        lo = None
        hi = None
        while n_idx < db.numbers.size:
            n = db.numbers[n_idx]
            if n['street_id'] != street_id:
                break
            if n['number'] == number:
                return Result.from_plate(db, n_idx, max_score)
            if n['number'] < number:
                lo = n_idx
            elif not hi:
                hi = n_idx
            n_idx += 1

        # exact number was not found => interpolate address position
        if lo:
            n = db.numbers[lo]
            lon, lat = reverse_geohash(n['geohash'])
            return Result.from_interpolated(db, number, street_id, lon, lat)
        else:
            n = db.numbers[hi]
            lon, lat = reverse_geohash(n['geohash'])
            return Result.from_interpolated(db, number, street_id, lon, lat)

    else:
        # middle of the street
        n_idx_hi = find(street_id, db.numbers['street_id'])
        n_idx_lo = n_idx_hi
        while n_idx_hi < db.numbers.size:
            n = db.numbers[n_idx_hi]
            if n['street_id'] != street_id:
                break
            n_idx_hi += 1
        n_idx = (n_idx_lo + n_idx_hi) // 2
        return Result.from_street(db, n_idx)


def search_by_insee(db, code_insee_list, code_post, query):
    query = unidecode(query)
    query = query.upper()
    query = clean_query(query)

    number = get_number(query)
    query = query.replace(str(number), '')
    query = ' '.join(query.split())  # remove multiple spaces

    street_id, score_street = search_street(db, code_insee_list, code_post,
                                            query)
    locality_id, score_locality = search_locality(db, code_insee_list, query,
                                                  score_street)
    max_score = max(score_street, score_locality)

    if not street_id and not locality_id:
        if len(code_insee_list) == 1:
            return Result.from_city(db, code_insee_list[0])
        else:
            return Result.from_code_post(db, code_post)

    return search_number(db, street_id, locality_id, number, max_score)


def search_by_zip_and_city(db, code_post, city, query):
    start = time.time()
    result = None
    code_post = code_post.zfill(5)
    code_insee = search_insee(db, code_post, city)
    if code_insee:
        result = search_by_insee(db, [code_insee], code_post, query)
    else:
        code_insee_pos = find_all_from_index(code_post,
                                             db.cities_post_index,
                                             db.cities['code_post'],
                                             string=True)
        code_insee_list = [db.cities[pos]['code_insee'].decode('UTF-8') for
                           pos in code_insee_pos]
        if len(code_insee_list) > 0:
            result = search_by_insee(db, code_insee_list, code_post, query)
        else:
            result = Result.from_error('Could not find the city for this '
                                       'address.')
    result.set_time(time.time() - start)
    return result


if __name__ == '__main__':
    from db import AddressDatabase
    db = AddressDatabase()
    # for i in range(100):
    #     idx = db.cities_post_index[i]
    #     try:
    #         print(idx, db.cities[idx])
    #     except:
    #         print(idx, ' invalid index')

    # t1 = time.time()
    print(search_by_zip_and_city(
        db, '91120', 'PALAISEAU', '12 BD DES MARECHAUX').to_json())
    print(search_by_zip_and_city(
        db, '91120', 'PALAISEAU', '13 BD DES MARECHAUX').to_json())
    print(search_by_zip_and_city(
        db, '91120', 'PALAISEAU', '14 BD DES MARECHAUX').to_json())
    # print(search_by_zip_and_city(
    #     db, '33000', 'BORDEAUX', '303 BD Du PReSIDenT WILSON').to_json())
    # print(search_by_zip_and_city(
    #     db, '44300', 'Nantes', '40 rue de la cognardière').to_json())
    # print(search_by_zip_and_city(
    #     db, '58400', 'narcy', 'Le boisson').to_json())
    # print(search_by_zip_and_city(
    #     db, '75013', 'PARIS', '7 PLACE DE RUNGIS').to_json())
    # print(search_by_zip_and_city(
    #     db, '78500', 'sartrouville', '').to_json())
    # print(search_by_zip_and_city(
    #     db, '93152', 'LE BLANC MESNIL CEDEX',
    #     '15 AV CHARLES DE GAULLE',).to_json())
    # print(search_by_zip_and_city(
    #     db, '13080', 'LUYNES',
    #     '685 CH DE LA COMMANDERIE DE  ST JEAN DE MALTES',).to_json())
    # print(search_by_zip_and_city(
    #     db, '60800', 'TRUMILLY',
    #     'LE PLESSIS CORNEFROY 3 RUE DE BEAURAIN',).to_json())
    # print(search_by_zip_and_city(
    #     db, '75116', 'PARIS', '198 AV VICTOR HUGO',).to_json())
    # print(search_by_zip_and_city(
    #     db, '75015', 'PARIS', '140 RUE SAINT CHARLES',).to_json())
    # print(search_by_zip_and_city(
    #     db, '44150', 'ST HERBLON', '16 RUE DU FORT',).to_json())
    # print(search_by_zip_and_city(
    #     db, '59285', 'ARNEKE', '2 ROUTE DE WORMHOUT').to_json())
    # t2 = time.time()
    # print(t2 - t1)
