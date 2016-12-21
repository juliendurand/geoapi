from datetime import datetime
import traceback

import pandas as pd

import main
import search
from utils import haversine


def batch(db):
    # in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    in_file = 'data/ADRESSES_PART_GEO_AMABIS_v01072016_out.csv'
    out_file = 'data/ADRESSES_PART_GEO_AMABIS_v01072016_geocoding_julien.csv'
    total_error = 0
    with open(in_file, 'r',encoding='UTF-8') as addresses, \
            open(out_file, 'w',encoding='UTF-8') as out:
        
        for i, line in enumerate(addresses):
            line = line[:-1].replace('"', '')
            if i == 0:
                out.write(line+';locality;number;street;code_post;city;code_insee;country;quality;distance;error;lon;lat;time\n')
                continue
            values = line.split(';')
            try:
                code_post = values[5].zfill(5)
                city = values[6]
                query = values[3] or values[2] or values[1]
                address = search.search_by_zip_and_city(db, code_post, city,
                                                      query).to_address()
                d = 100000
                if values[32] and values[33]:
                    if address['lon'] and address['lat']:
                        lon1 = float(values[32])
                        lat1 = float(values[33])
                        lon2 = float(address['lon'])
                        lat2 = float(address['lat'])
                        d = haversine(lon1, lat1, lon2, lat2)
                    else:
                        d = 0
                    if d == 100000:
                        print(i)
                    error = d
                    values += [
                        address['locality'],
                        address['number'],
                        address['street'],
                        address['code_post'],
                        address['city'],
                        address['code_insee'],
                        address['country'],
                        address['quality'].value,
                        str(round(d, 2)),
                        str(round(error, 6)),
                        address['lon'],
                        address['lat'],
                        address['time'],
                        ]
                    total_error += error
            except Exception as e:
                print(e)
                traceback.print_exc()
            out.write(";".join(map(str, values)) + '\n')
            if i % 1000 == 0:
                print(i, 'th ERROR: ', round(total_error/(i-1), 2))
        print('FINAL ERROR: ', round(total_error/(i-1), 2))


def batch2(db):
    # in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    out_file = 'data/adresses_vAMABIS_v28092016_out_v2_geocoding_julien.csv'
    total_error = 0
    with open(in_file, 'r',encoding='UTF-8') as addresses, \
            open(out_file, 'w',encoding='UTF-8') as out:
        for i, line in enumerate(addresses):
            line = line[:-1].replace('"', '')
            if i == 0:
                out.write(line+';locality;number;street;code_post;city;code_insee;country;quality;distance;error;lon;lat;time\n')
                continue
            values = line.split(';')
            try:
                code_post = values[5].zfill(5)
                city = values[6]
                query = values[3] or values[2] or values[1]
                address = search.search_by_zip_and_city(db, code_post, city,
                                                        query).to_address()
                d = 100000
                if values[31] and values[32]:
                    if address['lon'] and address['lat']:
                        lon1 = float(values[31])
                        lat1 = float(values[32])
                        lon2 = float(address['lon'])
                        lat2 = float(address['lat'])
                        d = haversine(lon1, lat1, lon2, lat2)
                else:
                    d = 0
                if d == 100000:
                    print(i)
                error = d
                values += [
                    address['locality'],
                    address['number'],
                    address['street'],
                    address['code_post'],
                    address['city'],
                    address['code_insee'],
                    address['country'],
                    address['quality'].value,
                    str(round(d, 2)),
                    str(round(error, 6)),
                    address['lon'],
                    address['lat'],
                    address['time'],
                    ]
                total_error += error
            except Exception as e:
                print(e)
                traceback.print_exc()
            out.write(";".join(map(str, values)) + '\n')
            if i % 1000 == 0:
                print(i, 'th ERROR: ', round(total_error/(i-1), 2))
        print('FINAL ERROR: ', round(total_error/(i-1), 2))


def calculate_metrics():
    out_file = 'data/adresses_vAMABIS_v28092016_out_v2_geocoding_julien.csv'
    df = pd.read_csv(out_file, delimiter=';')
    metrics = df.groupby('quality')['error'].agg(['count', 'sum', 'mean', 'std','min','median', 'max' ])
    print(metrics)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    metrics.to_csv('data/metrics/metrics %s.csv' % timestamp)
    metrics = df.groupby(['quality', 'STACOORD'])['error'].agg(['count', 'sum', 'mean', 'std','min','median', 'max' ])
    metrics.to_csv('data/metrics/metrics_detailed %s.csv' % timestamp)
    print(df[df['quality'] == 1]['error'].describe())
    print(df.groupby(['STACOORD'])['error'].agg(['count', 'sum', 'mean', 'std','min','median', 'max' ]))


def save_big_error():
    out_file = 'data/adresses_vAMABIS_v28092016_out_v2_geocoding_julien.csv'
    df = pd.read_csv(out_file, delimiter=';')
    df[df['error'] > 1000].to_csv('data/big_error.csv')


if __name__ == '__main__':
    db = main.AddressDatabase()
    batch(db)
    batch2(db)
    #calculate_metrics()
    #save_big_error()
