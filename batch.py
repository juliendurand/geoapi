import main
from utils import haversine


def batch(db):
    # in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    in_file = 'data/ADRESSES_PART_GEO_AMABIS_v01072016_out.csv'
    out_file = 'data/ADRESSES_PART_GEO_AMABIS_v01072016_geocoding_julien.csv'
    with open(in_file, 'r') as addresses, \
            open(out_file, 'w') as out:
        i = 0
        for line in addresses:
            line = line[:-1].replace('"', '')
            if i == 0:
                out.write(line+';locality;number;street;code_post;city;code_insee;country;distance;lon;lat;time\n')
                i = 1
                continue
            values = line.split(';')
            try:
                code_post = values[5].zfill(5)
                city = values[6]
                query = values[3]
                address = main.search_by_zip_and_city(db, code_post, city,
                                                      query)
                d = None
                if address['lon'] != 'None' and address['lat'] != 'None':
                    lon1 = float(values[32])
                    lat1 = float(values[33])
                    lon2 = float(address['lon'])
                    lat2 = float(address['lat'])
                    d = haversine(lon1, lat1, lon2, lat2)
                values += [
                    address['locality'],
                    address['number'],
                    address['street'],
                    address['code_post'],
                    address['city'],
                    address['code_insee'],
                    address['country'],
                    str(d),
                    address['lon'],
                    address['lat'],
                    address['time'],
                    ]
            except:
                pass
            out.write(";".join(map(str, values)) + '\n')


def batch2(db):
    # in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    in_file = 'data/adresses_vAMABIS_v28092016_out_v2.csv'
    out_file = 'data/adresses_vAMABIS_v28092016_out_v2_geocoding_julien.csv'
    with open(in_file, 'r') as addresses, \
            open(out_file, 'w') as out:
        i = 0
        for line in addresses:
            line = line[:-1].replace('"', '')
            if i == 0:
                out.write(line+';locality;number;street;code_post;city;code_insee;country;distance;lon;lat;time\n')
                i = 1
                continue
            values = line.split(';')
            try:
                code_post = values[5].zfill(5)
                city = values[6]
                query = values[3]
                address = main.search_by_zip_and_city(db, code_post, city,
                                                      query)
                d = None
                if address['lon'] != 'None' and address['lat'] != 'None':
                    lon1 = float(values[31])
                    lat1 = float(values[32])
                    lon2 = float(address['lon'])
                    lat2 = float(address['lat'])
                    d = haversine(lon1, lat1, lon2, lat2)
                values += [
                    address['locality'],
                    address['number'],
                    address['street'],
                    address['code_post'],
                    address['city'],
                    address['code_insee'],
                    address['country'],
                    str(d),
                    address['lon'],
                    address['lat'],
                    address['time'],
                    ]
            except:
                pass
            out.write(";".join(map(str, values)) + '\n')


if __name__ == '__main__':
    db = main.AddressDatabase()
    batch()
    batch2(db)
