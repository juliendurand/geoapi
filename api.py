import importlib
import json

from flask import Flask, request

import main
import reverse
import utils


db = main.load_db()
kd_tree = reverse.kd_tree_index(db)

app = Flask(__name__)


@app.route('/distance')
def distance():
    # in meters
    lon1 = float(request.args.get('lon1'))
    lat1 = float(request.args.get('lat1'))
    lon2 = float(request.args.get('lon2'))
    lat2 = float(request.args.get('lat2'))
    d = round(utils.haversine(lon1, lat1, lon2, lat2), 2)
    return json.dumps(d)


@app.route('/search')
def search():
    return 'ok'


@app.route('/reload')
def reload():
    importlib.reload(main)
    return 'ok'


@app.route('/reverse', methods=['GET', 'POST'])
def get_reverse():
    if request.method == 'GET':
        lon = float(request.args.get('lon'))
        lat = float(request.args.get('lat'))
        return json.dumps(reverse.reverse(kd_tree, db, lon, lat))
    elif request.method == 'POST':
        data = request.data.decode('utf-8')
        data = json.loads(data)
        results = []
        for line in data:
            lon = line[0]
            lat = line[1]
            results.append({
                           'lon': lon,
                           'lat': lat,
                           'address': reverse.reverse(kd_tree, db, lon, lat)
                           })
        return json.dumps(results)


if __name__ == '__main__':
    app.run()
