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

import time
import traceback
import psycopg2

import utils

conn = psycopg2.connect('dbname=Axa')
cur = conn.cursor()

zone_sec_encoding = {
    '': 0,
    'Faible': 1,
    'Moyen': 2,
    'Fort': 3,
}


def spatial_join(x, y, table, fields, numeric=True):
    cur.execute(("select %s from %s where ST_Contains(geom, " +
                "ST_GeomFromText('POINT(%s %s)'))") %
                (', '.join(fields), table, str(x), str(y)))
    rows = cur.fetchall()
    if len(rows) == 0 or len(rows[0]) == 0:
        return ''
    result = [int(value) if numeric else value for value in rows[0]]
    if len(result) == 1:
        return result[0]
    return result


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
        ['zonier_inc', 'zonier_i_1']) or (0, 0,)

    zone_sec = spatial_join(x, y, 'sec', ['alea'],
                            numeric=False)
    zone_sec = zone_sec_encoding[zone_sec]

    zone_flood = spatial_join(x, y, 'flood', ['zone_flood'])

    zone_coastal_flood = spatial_join(x, y, 'coastal_flood',
                                      ['scale']) or 0

    return {
        'zone_dde_a_f': zone_dde_a_f,
        'zone_dde_a_c': zone_dde_a_c,
        'zone_dde_m_f': zone_dde_m_f,
        'zone_dde_m_c': zone_dde_m_c,
        'zone_bdg_f': zone_bdg_c,
        'zone_bdg_c': zone_bdg_c,
        'zone_clim': zone_clim,
        'zone_vol_f': zone_vol_f,
        'zone_vol_c': zone_vol_c,
        'zone_incattr_f': zone_incattr_f,
        'zone_incattr_c': zone_incattr_c,
        'zone_sec': zone_sec,
        'zone_flood': zone_flood,
        'zone_coastal_flood': zone_coastal_flood,
    }


def batch(in_file, out_file):
    with open(in_file, 'r', encoding='UTF-8') as addresses, \
            open(out_file, 'w', encoding='UTF-8') as out:
        header = addresses.readline()[:-1].replace('"', '')
        separator = utils.detect_separator(header)
        headers = header.split(separator)
        lon_index = headers.index('LON')
        lat_index = headers.index('LAT')
        insee_index = headers.index('code_insee')
        iris_index = headers.index('code_iris')
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
        ]
        out.write(separator.join(headers + new_headers) + '\n')
        start_full = time.time()
        for i, line in enumerate(addresses):
            line = line[:-1].replace('"', '')
            values = line.split(';')
            try:
                if values[lon_index] and values[lat_index]:
                    lon = float(values[lon_index])
                    lat = float(values[lat_index])
                    x, y = utils.conv_wsg84_to_lambert93(lon, lat)
                    code_iris = values[iris_index]
                    code_insee = values[insee_index]
                    zones = get_zones(x, y, code_insee, code_iris)
                values += [zones[col] for col in new_headers]
            except Exception:
                traceback.print_exc()
            out.write(";".join(map(str, values)) + '\n')
            if (i + 1) % 1000 == 0:
                duration = time.time() - start_full
                print(i + 1, 'th time: ', round(duration, 2),
                      round(duration / (i + 1), 6))


if __name__ == '__main__':
    batch('data/geocoding_1.csv',
          'data/spatial_join_1.csv')
    batch('data/geocoding_2.csv',
          'data/spatial_join_2.csv')
