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

    print('address quality', address.quality.value)
    if 0 >= address.quality.value or address.quality.value >= 4:
        return None
    x = address.x
    y = address.y
    zones = spatial_join.get_zones_from_address(address)
    risks = [
        {
            'name': 'dde_a_f',
            'label': 'Fréquence Dégats des eaux - Appartement',
            'zone': zones['zone_dde_a_f'],
            'zone_max': max_zones['zone_dde_a_f_max'],
            'geo_json': get_polygons('dde_a', 'quant_f_01',
                                     max_zones['zone_dde_a_f_max'], x, y),
        },
        {
            'name': 'dde_a_c',
            'label': 'Coût Dégats des eaux - Appartement',
            'zone': zones['zone_dde_a_c'],
            'zone_max': max_zones['zone_dde_a_c_max'],
            'geo_json': get_polygons('dde_a', 'quant_cm_1',
                                     max_zones['zone_dde_a_c_max'], x, y),
        },
        {
            'name': 'dde_m_f',
            'label': 'Fréquence Dégats des Eaux - Maison',
            'zone': zones['zone_dde_m_f'],
            'zone_max': max_zones['zone_dde_m_f_max'],
            'geo_json': get_polygons('dde_m', 'quant_freq',
                                     max_zones['zone_dde_m_f_max'], x, y),
        },
        {
            'name': 'dde_m_c',
            'label': 'Coût Dégats des Eaux - Maison',
            'zone': zones['zone_dde_m_c'],
            'zone_max': max_zones['zone_dde_m_c_max'],
            'geo_json': get_polygons('dde_m', 'quant_cm_2',
                                     max_zones['zone_dde_m_c_max'], x, y),
        },
        {
            'name': 'bdg_f',
            'label': 'Fréquence Bris de Glace',
            'zone': zones['zone_bdg_c'],
            'zone_max': max_zones['zone_bdg_c_max'],
            'geo_json': get_polygons('bdg', 'quant_f_01',
                                     max_zones['zone_bdg_c_max'], x, y),
        },
        {
            'name': 'bdg_c',
            'label': 'Coût Bris de Glace',
            'zone': zones['zone_bdg_c'],
            'zone_max': max_zones['zone_bdg_c_max'],
            'geo_json': get_polygons('bdg', 'quant_cm_2',
                                     max_zones['zone_bdg_c_max'], x, y),
        },
        {
            'name': 'clim',
            'label': 'Tempête',
            'zone': zones['zone_clim'],
            'zone_max': max_zones['zone_clim_max'],
            'geo_json': get_polygons('clim', 'q95_xws',
                                     max_zones['zone_clim_max'], x, y)
        },
        {
            'name': 'vol_f',
            'label': 'Fréquence Vol',
            'zone': zones['zone_vol_f'],
            'zone_max': max_zones['zone_vol_f_max'],
            'geo_json': spatial_join.get_iris_polygons('vol_f',
                                                       'zone_vol_f_amelioree',
                                                       max_zones['zone_vol_f_max'],
                                                       'INSEE_COM',
                                                       x, y),
        },
        {
            'name': 'vol_c',
            'label': 'Coût Vol',
            'zone': zones['zone_vol_c'],
            'zone_max': max_zones['zone_vol_c_max'],
            'geo_json': spatial_join.get_iris_polygons('vol_c',
                                                       'zone_vol_c_amelioree',
                                                       max_zones['zone_vol_f_max'],
                                                       'INSEE_COM',
                                                       x, y),
        },
        {
            'name': 'incattr_f',
            'label': 'Fréquance Incendie',
            'zone': zones['zone_incattr_f'],
            'zone_max': max_zones['zone_incattr_f_max'],
        },
        {
            'name': 'incattr_c',
            'label': 'Coût Incendie',
            'zone': zones['zone_incattr_c'],
            'zone_max': max_zones['zone_incattr_c_max'],
        },
        {
            'name': 'sec',
            'label': 'Sécheresse',
            'zone': zones['zone_sec'],
            'zone_max': max_zones['zone_sec_max'],
        },
        {
            'name': 'flood',
            'label': 'Crue',
            'zone': zones['zone_flood'],
            'zone_max': max_zones['zone_flood_max'],
            'geo_json': get_polygons('flood', 'zone_flood',
                                     max_zones['zone_flood_max'], x, y),
        },
        {
            'name': 'coastal_flood',
            'label': 'Crue Côtière',
            'zone': zones['zone_coastal_flood'],
            'zone_max': max_zones['zone_coastal_flood_max'],
            'geo_json': get_polygons('coastal_flood', 'scale',
                                     max_zones['zone_coastal_flood_max'],
                                     x, y),
        },
    ]
    for risk in risks:
        risk['ratio'] = risk['zone'] / risk['zone_max']
    address.merge({'results': True, 'risks': risks})
    return address


def get_polygons(table, field, max_value, x, y):
    return spatial_join.get_polygons(table, field, max_value, x, y)
