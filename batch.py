from datetime import datetime
import traceback

import pandas as pd

from db import AddressDatabase
import spatial_join
import search
from utils import haversine, conv_wsg84_to_lambert93


def detect_separator(line):
    separator = None
    max_nb_tokens = 0
    for c in ',;#|:':
        nb_tokens = len(line.split(c))
        if nb_tokens > max_nb_tokens:
            separator = c
            max_nb_tokens = nb_tokens
    return separator


def batch(db, in_file, out_file):
    total_error = 0
    with open(in_file, 'r', encoding='UTF-8') as addresses, \
            open(out_file, 'w', encoding='UTF-8') as out:
        header = addresses.readline()[:-1].replace('"', '')
        separator = detect_separator(header)
        headers = header.split(separator)
        lon_index = headers.index('LON')
        lat_index = headers.index('LAT')
        new_headers = [
            'locality',
            'number',
            'street',
            'code_post',
            'city',
            'code_insee',
            'code_iris',
            'country',
            'quality',
            ' distance',
            'error',
            'lon',
            'lat',
            'time',
            'zone_dde_a_f',
            'zone_dde_a_c',
            'zone_dde_m_f',
            'zone_dde_m_c',
            'zone_bdg_f',
            'zone_bdg_c',
            'zone_clim',
            'zone_vol_f',
            'zone_vol_c',
            'zone_catnat',
            'zone_incattr_f',
            'zone_incattr_c',
        ]
        out.write(separator.join(headers + new_headers) + '\n')
        for i, line in enumerate(addresses):
            line = line[:-1].replace('"', '')
            values = line.split(';')
            try:
                code_post = values[5].zfill(5)
                city = values[6]
                # query = values[3] or values[2] or values[1]
                query = values[4]
                address = search.search_by_zip_and_city(db, code_post, city,
                                                        query).to_address()
                d = 100000

                if address['lon'] and address['lat']:
                    if values[lon_index] and values[lat_index]:
                        lon1 = float(values[lon_index])
                        lat1 = float(values[lat_index])
                        lon2 = float(address['lon'])
                        lat2 = float(address['lat'])
                        d = haversine(lon1, lat1, lon2, lat2)
                        x, y = conv_wsg84_to_lambert93(lon2, lat2)
                        zone_dde_a_f, zone_dde_a_c = spatial_join.spatial_join(
                            x, y, 'ddea', ['quant_f_01', 'quant_cm_1'])
                    else:
                        d = 0  # TO CHECK d=0 when unavailable values 32,33
                    if d >= 100000:
                        print(i, d)
                    error = d
                    total_error += error
                values += [
                    address['locality'],
                    address['number'],
                    address['street'],
                    address['code_post'],
                    address['city'],
                    address['code_insee'],
                    address['code_iris'],
                    address['country'],
                    address['quality'].value,
                    str(round(d, 2)),
                    str(round(error, 6)),
                    address['lon'],
                    address['lat'],
                    address['time'],
                    zone_dde_a_f,
                    zone_dde_a_c,
                ]
            except Exception as e:
                print(e)
                traceback.print_exc()
            out.write(";".join(map(str, values)) + '\n')
            if (i + 1) % 1000 == 0:
                print(i + 1, 'th ERROR: ', round(total_error / (i + 1), 2))
        print('FINAL ERROR: ', round(total_error / (i + 1), 2))


def calculate_metrics(filename):
    df = pd.read_csv(filename, delimiter=';')
    metrics = df.groupby('quality')['error'].agg(['count', 'sum', 'mean',
                                                  'std', 'min', 'median',
                                                  'max'])
    print(metrics)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    metrics.to_csv('data/metrics/metrics %s.csv' % timestamp)
    metrics = df.groupby(['quality', 'STACOORD'])['error'] \
                .agg(['count', 'sum', 'mean', 'std', 'min', 'median', 'max'])
    metrics.to_csv('data/metrics/metrics_detailed %s.csv' % timestamp)
    print(df[df['quality'] == 1]['error'].describe())
    print(df.groupby(['STACOORD'])['error'].agg(['count', 'sum', 'mean', 'std',
                                                 'min', 'median', 'max']))


def save_big_error(filename):
    df = pd.read_csv(filename, delimiter=';')
    df[df['error'] > 1000].to_csv('data/big_error.csv')


if __name__ == '__main__':
    db = AddressDatabase()
    batch(db, 'data/ADRESSES_PART_GEO_AMABIS_v01072016_out.csv',
          'data/ADRESSES_PART_GEO_AMABIS_v01072016_geocoding_julien.csv')
    batch(db, 'data/adresses_vAMABIS_v28092016_out_v2.csv',
          'data/adresses_vAMABIS_v28092016_out_v2_geocoding_julien.csv')
    calculate_metrics('data/adresses_vAMABIS_v28092016_out_v2_geocoding_julien.csv')
    save_big_error('data/adresses_vAMABIS_v28092016_out_v2_geocoding_julien.csv')
