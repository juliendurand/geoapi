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

import importlib
import json

from flask import Flask, request

import main
import reverse
import utils


db = main.AddressDatabase()
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
