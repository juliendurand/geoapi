import geopandas as gpd
from shapely.geometry import Point

from utils import conv_wsg84_to_lambert93

print('Loading IRIS Shapefile')
# iris = gpd.read_file('./data/CONTOURS-IRIS_2-1__SHP_LAMB93_FXX_2016-11-10/CONTOURS-IRIS/1_DONNEES_LIVRAISON_2015/CONTOURS-IRIS_2-1_SHP_LAMB93_FE-2015/CONTOURS-IRIS.shp')
iris = gpd.read_file('./data/Mix_Contours_IRIS_Communes_OSM/Mix_Contours_IRIS_Communes_OSM.shp')
print('Loaded IRIS Shapefile')

iris_index = {}
for idx, row in iris.iterrows():
    # insee = row['INSEE_COM']
    # code_iris = row['CODE_IRIS']
    # geometry = row['geometry']
    insee = row['depcom']
    code_iris = row['dcomiris']
    geometry = row['geometry']
    c = iris_index.get(insee)
    if c is None:
        c = {}
        iris_index[insee] = c
    c[code_iris] = geometry

print('Finished indexing IRIS')


def get_iris(insee, x, y):
    """
    x, y must be in Lambert93
    """
    iris_list = iris_index.get(str(insee))
    if iris_list is None or len(iris_list) == 0:
        raise Exception('Could not find IRIS for this INSEE code : ', insee)
    elif len(iris_list) == 1:
        return list(iris_list)[0]

    point = Point(x, y)
    for code_iris, geometry in iris_list.items():
        if geometry.contains(point):
            return code_iris

    # if we can not locate the point within an IRIS polygon, we return the
    # polygon with the closest centroïd !
    # TODO return a warning !
    match = None
    min_distance = 0
    for code_iris, geometry in iris_list.items():
        distance = point.distance(geometry)
        if match is None or min_distance > distance:
            match = code_iris
            min_distance = distance
    return match


def get_iris_from_insee(insee):
    iris_list = iris_index[str(insee)]
    if len(iris_list) == 0:
        raise Exception('Could not find IRIS for this INSEE code : ', insee)
    elif len(iris_list) == 1:
        return list(iris_list)[0]
    return None
