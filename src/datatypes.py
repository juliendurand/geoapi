# -*- coding: utf-8 -*-
"""Type of the numpy arrays that stored in the binary files.

This module contains the non-trivial types of the numpy arrays stored in the
'.dat' files.

Attributes:
    city_dtype (np.dtype): The type of the array that stores the cities.
    street_dtype (np.dtype): The type of the array that stores the streets.
    locality_dtype (np.dtype): The type of the array that stores the
        localities.
    number_dtype (np.dtype): The type of the array that stores the numbers.

"""

import numpy as np

city_dtype = np.dtype([
    ('code_insee', 'a5'),
    ('code_post', 'a5'),
    ('nom_commune', 'a45'),
    ('lon', 'int32'),
    ('lat', 'int32'),
])

street_dtype = np.dtype([
    ('street_id', 'int32'),
    ('code_insee', 'a5'),
    ('code_post', 'a5'),
    ('nom_voie', 'a32'),
])

locality_dtype = np.dtype([
    ('locality_id', 'int32'),
    ('code_insee', 'a5'),
    ('code_post', 'a5'),
    ('nom_ld', 'a80'),
])

number_dtype = np.dtype([
    ('street_id', 'int32'),
    ('locality_id', 'int32'),
    ('number', 'int16'),
    ('rep', 'int8'),
    ('geohash', 'uint64'),
])
