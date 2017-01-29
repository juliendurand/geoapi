# coding: utf-8

import src.db as db
import src.spatial_join as spatial_join
import src.search as search


db_address = db.AddressDatabase()
max_zones = spatial_join.get_max_zones()


def get_risk_audit(address, code_post, city):
    address = search.search_by_zip_and_city(db_address, code_post, city,
                                            address) \
                    .to_address()
    zones = spatial_join.get_zones_from_address(address)
    address.merge(zones)
    address.merge(max_zones)
    return address
