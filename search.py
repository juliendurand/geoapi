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

import difflib
import re

from address import to_address


def find(x, values):
    lo = 0
    hi = len(values)
    while lo < hi:
        mid = (lo+hi)//2
        midval = values[mid]
        if midval < x:
            lo = mid+1
        else:
            hi = mid
    return lo


def find_index(x, index, values, string=False):
    lo = 0
    hi = len(index)
    while lo < hi:
        mid = (lo+hi)//2
        midval = values[index[mid]]
        if string:
            midval = midval.decode('UTF-8')
        if midval < x:
            lo = mid+1
        else:
            hi = mid
    return lo


def find_all_from_index(x, index, values, string=False):
    idx = find_index(x, index, values, string)
    n = len(index)
    while idx < n:
        pos = index[idx]
        value = values[pos]
        if string:
            value = value.decode('UTF-8')
        if value != x:
            break
        yield pos
        idx += 1


def score_default(query, item):
    if not query:
        return 0
    query = query.upper()
    item = item.upper()
    query_set = set(query.split())
    item_set = set(item.split())
    intersection = query_set & item_set
    union = query_set | item_set
    return float(len(intersection))/len(union)
    #return difflib.SequenceMatcher(a=query.lower(),
    #                               b=street['nom'].lower()).   ratio()


def score_street(query, street):
    return score_default(query, street)


def score_locality(query, locality):
    return score_default(query, locality)


def score_city(query, city):
    return score_default(query, city)


def best_match(query, items, score, min_score=0):
    match = None
    max_score = min_score
    for i, item in enumerate(items):
        score = score_city(query, item)
        if score > max_score:
            match = i
            max_score = score
    return (match, max_score,)


def get_number(query):
    for token in re.findall(r'\d+', query):
        try:
            number = int(token)
            return number
        except:
            pass
    return 0


def search_insee(db, code_post, city):
    city_pos_list = find_all_from_index(code_post, db.cities_post_index,
                                        db.cities['code_post'], string=True)
    cities = [db.cities[pos] for pos in city_pos_list]
    names = [c['nom_commune'].decode('UTF-8') for c in cities]
    city, max_score = best_match(city, names, score_city)
    return cities[city]['code_insee'].decode('UTF-8') if city is not None else None


def search_by_insee(db, code_insee, query):
    result = None
    is_locality = False
    max_score = 0
    match_id = None

    # find street
    street_pos_list = find_all_from_index(code_insee, db.streets_insee_index,
                                          db.streets['code_insee'],
                                          string=True)
    streets = [db.streets[pos] for pos in street_pos_list]
    names = [s['nom_voie'].decode('UTF-8') for s in streets]
    street, max_score = best_match(query, names, score_street)
    if street is not None:
        match_id = streets[street]['street_id']

    # find locality
    locality_pos_list = find_all_from_index(code_insee,
                                            db.localities_insee_index,
                                            db.localities['code_insee'],
                                            string=True)
    localities = [db.localities[pos] for pos in locality_pos_list]
    names = [l['nom_ld'].decode('UTF-8') for l in localities]
    locality, max_score = best_match(query, names, score_locality,
                                     min_score=max_score)
    if locality is not None:
        match_id = localities[locality]['locality_id']
        is_locality = True

    if not match_id:
        return None

    if is_locality:
        result_idx = find_index(match_id, db.numbers_locality_index,
                                db.numbers['locality_id'])
        result = db.numbers_locality_index[result_idx]
    else:
        number = get_number(query)
        n_idx = find(match_id, db.numbers['street_id'])
        while True:
            n = db.numbers[n_idx]
            if n['street_id'] != match_id:
                break
            if n['number'] == number:
                result = n_idx
                break
            n_idx += 1
    return to_address(db, result)


def search_by_zip_and_city(db, code_post, city, query):
    import time
    start = time.time()
    code_insee = search_insee(db, code_post, city)
    print(time.time()-start)
    result = search_by_insee(db, code_insee, query)
    print(time.time()-start)
    if result:
        return result
    return

if __name__ == '__main__':
    import main
    db = main.AddressDatabase()
    print(search_by_zip_and_city(db, '58400', 'narcy', 'Le boisson'))  # '58189',
    print(search_by_zip_and_city(db, '78500', 'sartrouville', '10 Jules Ferry'))  # '78586',
