# coding: utf-8

import db
import spatial_join
import search


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


print(get_risk_audit('40 rue de la connardière', '44300', 'Nantes').to_json())
