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

import psycopg2

conn = psycopg2.connect('dbname=Axa')
cur = conn.cursor()


def spatial_join(x, y, table, fields):

    cur.execute("select %s from %s where ST_Contains(geom, ST_GeomFromText('POINT(%s %s)'))" % (', '.join(fields), table, x, y))
    rows = cur.fetchall()
    return [int(value) for value in rows[0]]
