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
    risks = [
        {
            'label': 'Dégats des eaux - Appartement',
            'zone': zones['zone_dde_a_f'],
            'zone_max': max_zones['zone_dde_a_f_max'],
        },
        {
            'label': 'Coût Dégats des eaux - Appartement',
            'zone': zones['zone_dde_a_c'],
            'zone_max': max_zones['zone_dde_a_c_max'],
        },
        {
            'label': 'Dégat des Eaux - Maison',
            'zone': zones['zone_dde_m_f'],
            'zone_max': max_zones['zone_dde_m_f_max'],
        },
        {
            'label': 'Coût Dégat des Eaux - Maison',
            'zone': zones['zone_dde_m_c'],
            'zone_max': max_zones['zone_dde_m_c_max'],
        },
        {
            'label': 'Bris de Glace',
            'zone': zones['zone_bdg_c'],
            'zone_max': max_zones['zone_bdg_c_max'],
        },
        {
            'label': 'Coût Bris de Glace',
            'zone': zones['zone_bdg_c'],
            'zone_max': max_zones['zone_bdg_c_max'],
        },
        {
            'label': 'Tempête',
            'zone': zones['zone_clim'],
            'zone_max': max_zones['zone_clim_max'],
        },
        {
            'label': 'Vol',
            'zone': zones['zone_vol_f'],
            'zone_max': max_zones['zone_vol_f_max'],
        },
        {
            'label': 'Coût Vol',
            'zone': zones['zone_vol_c'],
            'zone_max': max_zones['zone_vol_c_max'],
        },
        {
            'label': 'Incendie',
            'zone': zones['zone_incattr_f'],
            'zone_max': max_zones['zone_incattr_f_max'],
        },
        {
            'label': 'Coût Incendie',
            'zone': zones['zone_incattr_c'],
            'zone_max': max_zones['zone_incattr_c_max'],
        },
        {
            'label': 'Sécheresse',
            'zone': zones['zone_sec'],
            'zone_max': max_zones['zone_sec_max'],
        },
        {
            'label': 'Crue',
            'zone': zones['zone_flood'],
            'zone_max': max_zones['zone_flood_max'],
        },
        {
            'label': 'Crue Côtière',
            'zone': zones['zone_coastal_flood'],
            'zone_max': max_zones['zone_coastal_flood_max'],
        },
    ]
    for risk in risks:
        risk['ratio'] = risk['zone'] / risk['zone_max']
    address.merge({'risks': risks})
    return address
