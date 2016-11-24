import difflib
import re


def score_street(query, street):
    intersection = set(query.lower().split()) & \
        set(street.lower().split())
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


def find_index(x, index, values):
    lo = 0
    hi = len(index)
    while lo < hi:
        mid = (lo+hi)//2
        midval = values[index[mid]].decode('UTF-8')
        if midval < x:
            lo = mid+1
        else:
            hi = mid
    return lo


def search(db, code_insee, query):
    query = query.lower()

    match = None
    max_score = 0
    street_idx = find_index(code_insee, db.streets_insee_index,
                            db.streets['code_insee'])
    while True:
        street_id = db.streets_insee_index[street_idx]
        street = db.streets[street_id]
        if street['code_insee'].decode('UTF-8') != code_insee:
            break
        score = score_street(query, street['nom_voie'].decode('UTF-8'))
        if score > max_score:
            max_score = score
            match = street
        street_idx += 1
    street_id = match['street_id']

    number = get_number(query)
    number_match = None
    n_idx = find(street_id, db.numbers['street_id'])
    while True:
        n = db.numbers[n_idx]
        if n['street_id'] != street_id:
            break
        if n['number'] == number:
            number_match = n
            break
        n_idx += 1
    return {
        'code_insee': code_insee,
        'nom_voie': match['nom_voie'],
        'numero': number_match['number'] if number_match else "",
        'lat': number_match['lat'] if number_match else "",
        'lon': number_match['lon'] if number_match else "",
        }

if __name__ == '__main__':
    import main
    db = main.AddressDatabase()
    print(search(db, '78586', '10 Jules Ferry'))
