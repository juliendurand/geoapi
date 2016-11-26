import difflib
import re

from address import to_address


def score_street(query, street):
    intersection = set(query.lower().split()) & \
        set(street.lower().split())
    return len(intersection)
    #return difflib.SequenceMatcher(a=query.lower(),
    #                               b=street['nom'].lower()).   ratio()


def score_locality(query, locality):
    return score_street(query, locality)


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


def find_index(x, index, values, str=False):
    lo = 0
    hi = len(index)
    while lo < hi:
        mid = (lo+hi)//2
        midval = values[index[mid]]
        if str:
            midval = midval.decode('UTF-8')
        if midval < x:
            lo = mid+1
        else:
            hi = mid
    return lo


def search(db, code_insee, query):
    query = query.lower()
    result = None
    is_locality = False
    max_score = 0
    match_id = None

    street_id = None
    street_idx = find_index(code_insee, db.streets_insee_index,
                            db.streets['code_insee'], str=True)
    while True:
        street_id = db.streets_insee_index[street_idx]
        street = db.streets[street_id]
        if street['code_insee'].decode('UTF-8') != code_insee:
            break
        score = score_street(query, street['nom_voie'].decode('UTF-8'))
        if score > max_score:
            max_score = score
            match_id = street['street_id']
        street_idx += 1

    locality_id = None
    locality_idx = find_index(code_insee, db.localities_insee_index,
                              db.localities['code_insee'], str=True)
    while True:
        locality_id = db.localities_insee_index[locality_idx]
        locality = db.localities[locality_id]
        if locality['code_insee'].decode('UTF-8') != code_insee:
            break
        score = score_locality(query, locality['nom_ld'].decode('UTF-8'))
        if score > max_score:
            is_locality = True
            max_score = score
            match_id = locality['locality_id']
        locality_idx += 1

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

if __name__ == '__main__':
    import main
    db = main.AddressDatabase()
    print(search(db, '58189', 'Le boisson'))
    print(search(db, '78586', '10 Jules Ferry'))
