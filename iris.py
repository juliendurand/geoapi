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
conn.autocommit = True
cur = conn.cursor()


def get_iris(insee, x=None, y=None):
    """
    x, y must be in Lambert93
    """

    # city with a single iris
    cur.execute("SELECT dcomiris FROM iris WHERE depcom='%s'" % (insee,))
    rows = cur.fetchall()
    if len(rows) == 0:
        raise Exception('Could not find IRIS for this INSEE code : ', insee)
    elif len(rows) == 1:
        return rows[0][0]

    if x is None or y is None:
        return None

    # city with multiple iris
    cur.execute("SELECT dcomiris FROM iris WHERE depcom='%s' "
                "AND ST_Contains(geom, ST_GeomFromText('POINT(%s %s)'))" %
                (insee, x, y,))
    rows = cur.fetchall()
    if len(rows) > 1:
        raise Exception('Multiple IRIS matching for this INSEE code : ',
                        insee, ' with x, y : ', x, ' ', y, ' - ', list(rows))
    elif len(rows) == 1:
        return rows[0][0]

    # if we can not locate the point within an IRIS polygon, we return the
    # polygon with the min distance !
    cur.execute("SELECT dcomiris FROM iris WHERE depcom='%s' "
                "ORDER BY ST_Distance(geom, ST_GeomFromText('POINT(%s %s)')) "
                "LIMIT 1;" % (insee, x, y,))
    rows = cur.fetchall()
    return rows[0][0]
