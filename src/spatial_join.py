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

import json
import time
import traceback
import psycopg2

import src.utils as utils

conn = psycopg2.connect('dbname=Axa')
conn.autocommit = True
cur = conn.cursor()

zone_sec_encoding = {
    '': 0,
    'Faible': 1,
    'Moyen': 2,
    'Fort': 3,
}


def spatial_join(x, y, table, fields, numeric=True):
    cur.execute("select %s from %s where ST_Contains(geom, "
                "ST_GeomFromText('POINT(%s %s)')) " %
                (', '.join(fields), table, float(x), float(y)))
    rows = cur.fetchall()
    # print("nombre de lignes ", table, " ", len(rows))
    if len(rows) == 0 or len(rows[0]) == 0:
        return ''
    result = [int(value) if numeric else value for value in rows[0]]
    if len(result) == 1:
        return result[0]
    return result


def spatial_max(table, field, numeric=True):
    cur.execute("select max(%s) from %s" % (field, table))
    rows = cur.fetchall()
    return int(rows[0][0]) if numeric else rows[0][0]


def table_join(key, id, table, fields, numeric=True):
    cur.execute("select %s from %s where %s='%s'" %
                (', '.join(fields), table, key, id,))
    rows = cur.fetchall()
    if len(rows) == 0 or len(rows[0]) == 0:
        return ''
    result = [int(value) if numeric else value for value in rows[0]]
    if len(result) == 1:
        return result[0]
    return result


def get_zones(x, y, code_insee, code_iris):
    zone_dde_a_f, zone_dde_a_c = spatial_join(
        x, y, 'dde_a', ['quant_f_01', 'quant_cm_1'])

    zone_dde_m_f, zone_dde_m_c = spatial_join(
        x, y, 'dde_m', ['quant_freq', 'quant_cm_2'])

    zone_bdg_f, zone_bdg_c = spatial_join(
        x, y, 'bdg', ['quant_f_01', 'quant_cm_2'])

    zone_clim = spatial_join(x, y, 'clim', ['q95_xws'])

    zone_vol_f = table_join('INSEE_COM', code_insee, 'vol_f',
                            ['zone_vol_f_amelioree'])

    zone_vol_c = table_join('INSEE_COM', code_insee, 'vol_c',
                            ['zone_vol_c_amelioree'])

    zone_incattr_f, zone_incattr_c = table_join(
        'DCOMIRIS', code_iris, 'incattr',
        ['zonier_i_1', 'zonier_inc']) or (0, 0,)

    zone_sec = spatial_join(x, y, 'sec', ['alea'],
                            numeric=False)
    zone_sec = zone_sec_encoding[zone_sec]

    zone_flood = spatial_join(x, y, 'flood', ['zone_flood'])

    zone_coastal_flood = spatial_join(x, y, 'coastal_flood',
                                      ['scale']) or 0
#Ajout zonier

    zone_clim_int = spatial_join(x, y, 'clim_int', ['quant_pp_2'])

    zone_cat_int = spatial_join(x, y, 'cat_int', ['quant_pp_1'])


    return {
        'zone_dde_a_f': zone_dde_a_f,
        'zone_dde_a_c': zone_dde_a_c,
        'zone_dde_m_f': zone_dde_m_f,
        'zone_dde_m_c': zone_dde_m_c,
        'zone_bdg_f': zone_bdg_f,
        'zone_bdg_c': zone_bdg_c,
        'zone_clim': zone_clim,
        'zone_vol_f': zone_vol_f,
        'zone_vol_c': zone_vol_c,
        'zone_incattr_f': zone_incattr_f,
        'zone_incattr_c': zone_incattr_c,
        'zone_sec': zone_sec,
        'zone_flood': zone_flood,
        'zone_coastal_flood': zone_coastal_flood,

        #Ajout Sébastien
        'zone_clim_int': zone_clim_int,
        'zone_cat_int': zone_cat_int,

    }


def get_zones_from_address(address):
    x = address.x
    y = address.y
    code_insee = address.code_insee
    code_iris = address.code_iris
    return get_zones(x, y, code_insee, code_iris)


def get_max_zones():
    return {
        'zone_dde_a_f_max': spatial_max('dde_a', 'quant_f_01'),
        'zone_dde_a_c_max': spatial_max('dde_a', 'quant_cm_1'),
        'zone_dde_m_f_max': spatial_max('dde_m', 'quant_freq'),
        'zone_dde_m_c_max': spatial_max('dde_m', 'quant_cm_2'),
        'zone_bdg_f_max': spatial_max('bdg', 'quant_f_01'),
        'zone_bdg_c_max': spatial_max('bdg', 'quant_cm_2'),
        'zone_clim_max': spatial_max('clim', 'q95_xws'),
        'zone_vol_f_max': spatial_max('vol_f', 'zone_vol_f_amelioree'),
        'zone_vol_c_max': spatial_max('vol_c', 'zone_vol_c_amelioree'),
        'zone_incattr_f_max': spatial_max('incattr', 'zonier_i_1'),
        'zone_incattr_c_max': 7,  # FIXME spatial_max('incattr', 'zonier_inc'),
        'zone_sec_max': 3,
        'zone_flood_max': spatial_max('flood', 'zone_flood'),
        'zone_coastal_flood_max': spatial_max('coastal_flood', 'scale'),

        #Ajout Sébastien
        'zone_clim_int_max': spatial_max('clim_int', 'quant_pp_2'),
        'zone_cat_int_max': spatial_max('cat_int', 'quant_pp_1'),
    }


def get_polygons(table, field, max_value, x, y):
    cur.execute("select %s, ST_AsGeoJSON(geom)  from %s "
                "order by geom <-> ST_GeomFromText('POINT(%s %s)') "
                "limit 5000" %
                (field, table, float(x), float(y)))
    # cur.execute("select %s, ST_AsGeoJSON(geom) from %s "
    #             "where ST_DWithin(geom, "
    #             "ST_GeomFromText('POINT(%s %s)'), 3000)" %
    #             (field, table, float(x), float(y)))
    rows = cur.fetchall()
    results = []
    print("nombre polygons for %s : " % table, len(rows))
    for row in rows:
        value = float(row[0]) / max_value
        geometry = row[1]
        results.append(geojson_to_feature(geometry, values={"risk": value}))
    results = {
        "type": "FeatureCollection",
        "features": results,
    }
    return json.dumps(results)


def get_iris_polygons(table, field, max_value, join_field, x, y):
    cur.execute("SELECT %s, ST_AsGeoJSON(geom) "
                "FROM iris INNER JOIN %s ON iris.DEPCOM = %s.%s "
                "ORDER BY geom <-> ST_GeomFromText('POINT(%s %s)') "
                "LIMIT 1000" %
                (field, table, table, join_field, float(x), float(y)))
    rows = cur.fetchall()
    results = []
    print("nombre de polygons for iris table : ", len(rows))
    for row in rows:
        value = float(row[0]) / max_value
        geometry = row[1]
        results.append(geojson_to_feature(geometry, values={"risk": value}))
    results = {
        "type": "FeatureCollection",
        "features": results,
    }
    return json.dumps(results)


def geojson_to_feature(geometry, values):
    geometry = json.loads(geometry)
    if geometry['type'] == 'MultiPolygon':
        points = geometry['coordinates'][0][0]
        points = [utils.conv_lambert93_to_wsg84(point[0], point[1])
                  for point in points]
        geometry['coordinates'][0][0] = points
    elif geometry['type'] == 'Polygon':
        points = geometry['coordinates'][0]
        points = [utils.conv_lambert93_to_wsg84(point[0], point[1])
                  for point in points]
        geometry['coordinates'][0] = points
    else:
        print('Unknown geometry : ', geometry['type'])

    return {
        "type": "Feature",
        "properties": values,
        "geometry": geometry,
    }


def json_geometry_to_polygon(geometry):
    geometry = json.loads(geometry)
    if geometry['type'] == 'MultiPolygon':
        points = geometry['coordinates'][0][0]
        points = [utils.conv_lambert93_to_wsg84(point[0], point[1], swap=True)
                  for point in points]
        return points
    else:
        print('UNKNOW geometry')


def batch(in_file, out_file):
    with open(in_file, 'r', encoding='UTF-8') as addresses, \
            open(out_file, 'w', encoding='UTF-8') as out:
        header = addresses.readline()[:-1].replace('"', '')
        separator = utils.detect_separator(header)
        headers = header.upper().split(separator)
        x_index = headers.index('XM')
        y_index = headers.index('YM')
        iris_index = headers.index('CODIRIS')

        new_headers = [
            'zone_dde_a_f',
            'zone_dde_a_c',
            'zone_dde_m_f',
            'zone_dde_m_c',
            'zone_bdg_f',
            'zone_bdg_c',
            'zone_clim',
            'zone_vol_f',
            'zone_vol_c',
            'zone_incattr_f',
            'zone_incattr_c',
            'zone_sec',
            'zone_flood',
            'zone_coastal_flood',
            'zone_clim_int',
            'zone_cat_int',
        ]
        out.write(separator.join(headers + new_headers) + '\n')

        start_full = time.time()
        for i, line in enumerate(addresses):
            line = line[:-1].replace('"', '')
            values = line.split(separator)
            try:
                x = values[x_index]
                y = values[y_index]
                code_iris = values[iris_index]
                code_insee = code_iris[:5]
                zones = get_zones(x, y, code_insee, code_iris)
                values += [zones[col] for col in new_headers]
            except Exception:
                traceback.print_exc()
            out.write(separator.join(map(str, values)) + '\n')
            if (i + 1) % 1000 == 0:
                duration = time.time() - start_full
                print(i + 1, 'th time: ', round(duration, 2),
                      round(duration / (i + 1), 6))


if __name__ == '__main__':
    pass
    #print(get_max_zones())
    # batch('data/contracts/contrats_3_geocodes.csv',
    #       'data/results/contracts_zones_march.csv')
    # batch('data/geocoding_1.csv',
    #       'data/spatial_join_1.csv')
    # batch('data/geocoding_2.csv',
    #       'data/spatial_join_2.csv')
