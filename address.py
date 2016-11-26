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

from utils import int_to_degree


def to_plain_address(locality, number, street, code_post, city, country):
    address = []
    if locality:
        address.append(locality)
    elif street:
        address.append(str(number) + ' ' + street)
    address.append(code_post + ' ' + city)
    address.append(country)
    return address


def to_address(db, idx, distance=None):
    n = db.numbers[idx]
    street_id = n['street_id']
    locality_id = n['locality_id']
    street = db.streets[street_id]

    code_insee = street['code_insee']
    city_arg = db.cities['code_insee'].searchsorted(code_insee)
    city = db.cities[city_arg]

    locality = db.localities[locality_id]['nom_ld'].decode('UTF-8')
    number = int(n['number'])
    nom_voie = street['nom_voie'].decode('UTF-8')
    code_post = city['code_post'].decode('UTF-8')
    nom_commune = city['nom_commune'].decode('UTF-8')
    code_insee = code_insee.decode('UTF-8')
    country = 'FRANCE'
    lon = int_to_degree(n['lon'])
    lat = int_to_degree(n['lat'])

    response = {
        'locality': locality,
        'number': number,
        'street': nom_voie,
        'code_post': code_post,
        'city': nom_commune,
        'code_insee': code_insee,
        'country': country,
        'lon': lon,
        'lat': lat,
    }
    if distance:
        response['distance'] = round(distance, 2)

    response['text'] = to_plain_address(locality, number, nom_voie, code_post,
                                        nom_commune, country)

    return response