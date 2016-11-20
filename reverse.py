import numpy as np
from scipy.spatial import KDTree

from utils import degree_to_int, int_to_degree, haversine


def to_address(db, idx):
    n = db['numbers'][idx]
    street_id = n['street_id']
    street = db['streets'][street_id]
    code_insee = street['code_insee']
    c = db['cities']
    city_arg = c['code_insee'].searchsorted(code_insee)
    return str(n) + str(street) + str(c[city_arg])


def kd_tree_index(db):
    locations = db['numbers']['location']
    data = np.dstack((locations['lon'], locations['lat']))[0]
    kd_tree = KDTree(data, leafsize=10000)
    return kd_tree


def reverse(kd_tree, db, lon, lat):
    d, idx = kd_tree.query([[degree_to_int(lon), degree_to_int(lat)]], k=100)  # /!\ euclidean distance

    """calculate haversine distance to get the real orthonormic distance"""
    results = {}
    for hyp in idx[0]:
        pos = db['numbers'][hyp]['location']
        hlon = int_to_degree(pos['lon'])
        hlat = int_to_degree(pos['lat'])
        d = haversine(hlon, hlat, lon, lat)
        results[d] = to_address(db, hyp)
    for i in sorted(results):
        print(i, results[i])
    #return to_address(db, idx[0])
