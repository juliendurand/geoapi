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
import time

from unidecode import unidecode

from address import to_address
from utils import soundex, haversine
from trigram import Trigram


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


def best_match(query, items, min_score=0):
    t = Trigram(query.upper())
    match = None
    max_score = min_score
    for i, item in enumerate(items):
        score = t.score(item)
        if score == 1.0:
            return (i, 1.0,)
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


def get_repetition(query):
    # TODO
    pass


def search_insee(db, code_post, city):
    city_pos_list = find_all_from_index(code_post, db.cities_post_index,
                                        db.cities['code_post'], string=True)
    cities = [db.cities[pos] for pos in city_pos_list]
    names = [c['nom_commune'].decode('UTF-8') for c in cities]
    city, max_score = best_match(city, names)
    return cities[city]['code_insee'].decode('UTF-8') if city is not None else None


def search_by_insee(db, code_insee, query):
    query = unidecode(query)
    result = None
    is_locality = False
    max_score = 0
    match_id = None
    number = get_number(query)

    # find street
    if number:
        street_pos_list = find_all_from_index(code_insee, db.streets_insee_index,
                                              db.streets['code_insee'],
                                              string=True)
        streets = [db.streets[pos] for pos in street_pos_list]
        names = [s['nom_voie'].decode('UTF-8') for s in streets]
        street, max_score = best_match(query, names)
        if street is not None:
            match_id = streets[street]['street_id']

    # find locality
    locality_pos_list = find_all_from_index(code_insee,
                                            db.localities_insee_index,
                                            db.localities['code_insee'],
                                            string=True)
    localities = [db.localities[pos] for pos in locality_pos_list]
    names = [l['nom_ld'].decode('UTF-8') for l in localities]
    locality, max_score = best_match(query, names, min_score=max_score)
    if locality is not None:
        match_id = localities[locality]['locality_id']
        is_locality = True

    if not match_id:
        return None

    if is_locality:
        result_idx = find_index(match_id, db.numbers_locality_index,
                                db.numbers['locality_id'])
        result = db.numbers_locality_index[result_idx]
    elif number:
        n_idx = find(match_id, db.numbers['street_id'])
        while True:
            n = db.numbers[n_idx]
            if n['street_id'] != match_id:
                break
            if n['number'] == number:
                result = n_idx
                break
            n_idx += 1
    return result


def search_by_zip_and_city(db, code_post, city, query):
    start = time.time()
    result = None
    code_insee = search_insee(db, code_post, city)
    if code_insee:
        result = search_by_insee(db, code_insee, query)
    result = to_address(db, result)
    result['time'] = time.time()-start
    return result


def batch(db):
    # in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    in_file = 'data/ADRESSES_PART_GEO_AMABIS_v01072016_out.csv'
    with open(in_file, 'r') as addresses:
        i = 0
        for line in addresses:
            line = line[:-1].replace('"', '')
            if i == 0:
                print(line+';locality;number;street;code_post;city;code_insee;country;distance;lon;lat;time')
                i = 1
                continue
            values = line.split(';')
            try:

                code_post = values[5]
                city = values[6]
                query = values[3]
                address = search_by_zip_and_city(db, code_post, city, query)
                d = None
                if address['lon'] != 'None' and address['lat'] != 'None':
                    lon1 = float(values[32])
                    lat1 = float(values[33])
                    lon2 = float(address['lon'])
                    lat2 = float(address['lat'])
                    d = haversine(lon1, lat1, lon2, lat2)
                values += [
                    address['locality'],
                    address['number'],
                    address['street'],
                    address['code_post'],
                    address['city'],
                    address['code_insee'],
                    address['country'],
                    str(d),
                    address['lon'],
                    address['lat'],
                    address['time'],
                    ]
            except:
                pass
            print(";".join(map(str, values)))

if __name__ == '__main__':
    import main
    db = main.AddressDatabase()
    batch(db)
    #print(search_by_zip_and_city(db, '44300', 'Nantes', '40 rue de la cognardière')['text'])
    #print(search_by_zip_and_city(db, '58400', 'narcy', 'Le boisson')['text'])  # '58189',
    #print(search_by_zip_and_city(db, '78500', 'sartrouville', '10 Jules Ferry')['text'])  # '78586',
