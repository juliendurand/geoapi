from unidecode import unidecode
from utils import geohash, degree_to_int
import numpy as np


class LineProcessor():
    """Extract the information from a csv line and check if it is valid.

    This class allows the processing of a line from a csv file following the
    format specified by the BAN documentation. There is one csv file for each
    departement in France.

    Attributes:
        ok (boolean): True if the line has the good number of columns.
        numero (str): Address number.
        repetition (str): Address number complement.It is used to distinguesh
            addresses in the same street and with the same number (common in
            french addresses).
        code_insee (str): Unique code to each french commune.
        code_postal (str): Address zip code.
        nom_ld (str): Address locality (lieu-dit in french).
        nom_afnor (str): Route name following the postal service standard.
        commune (str): Commune name (similar to a city division).
        longitude (str): Longitude from address in string format.
        latitude (str): Latitude from address in string format.

    """

    def __init__(self, line):
        line = line.strip()
        line = line.replace('""', '')
        fields = line.split(';')

        self.ok = (len(fields) == 16)

        if self.ok:
            self.numero = fields[3]
            self.repetition = fields[4]
            self.code_insee = fields[5]
            self.code_postal = fields[6]
            self.nom_ld = unidecode(fields[8])
            self.nom_afnor = fields[9]
            self.commune = fields[10]
            self.longitude = fields[13]
            self.latitude = fields[14]

    def get_numero(self):
        return self.numero

    def get_repetition(self):
        return self.repetition

    def get_code_insee(self):
        return self.code_insee

    def get_code_postal(self):
        return self.code_postal

    def get_nom_ld(self):
        return self.nom_ld

    def get_nom_afnor(self):
        return self.nom_afnor

    def get_commune(self):
        return self.commune

    def get_longitude(self):
        return self.longitude

    def get_latitude(self):
        return self.latitude

    def is_ok(self):
        return self.ok

    def test(self):
        result = self.is_ok()
        result = result and self.test_numero()
        result = result and self.test_code_insee()
        result = result and self.test_code_postal()
        result = result and self.test_nom_ld()
        result = result and self.test_nom_afnor()
        result = result and self.test_commune()
        result = result and self.test_longitude()
        result = result and self.test_latitude()
        return result

    def test_numero(self):
        try:
            if int(self.numero) < 0:
                print('Invalid numero : "%s"' % self.numero)
                return False
        except ValueError:
            return False
        return True

    def test_code_insee(self):
        if len(self.code_insee) != 5:
            print('Invalid code_insee : "%s"' % self.code_insee)
            return False
        return True

    def test_code_postal(self):
        if len(self.code_postal) != 5:
            print('Invalid code_postal : "%s"' % self.code_postal)
            return False
        return True

    def test_nom_ld(self):
        if len(self.nom_ld) > 80:
            print('Invalid nom_ld : "%s"' % self.nom_ld)
            return False
        return True

    def test_nom_afnor(self):
        if len(self.nom_afnor) > 32:
            print('Invalid nom_afnor : "%s"' % self.nom_afnor)
        return True

    def test_commune(self):
        if len(self.commune) > 45:
            print('Invalid nom_commune : "%s"' % self.commune)
            return False
        return True

    def test_longitude(self):
        try:
            if not -180 <= float(self.longitude) <= 180:
                print('Invalid longitude: %s' % self.longitude)
                return False
        except ValueError:
            return False
        return True

    def test_latitude(self):
        try:
            if not -90 <= float(self.latitude) <= 90:
                print('Invalid latitude: %s' % self.latitude)
                return False
        except ValueError:
            return False
        return True
# --------------------------------------------------------------------------- #


class FileProcessor():
    """Extract the information from a csv file and writes a new ones.

    This class allows the processing of a csv file following the format
    specified by the BAN documentation. One instance of LineProcessor is used
    to extract the information of each line that is then used to write four new
    csv files: cities.csv, locality.csv, numbers.csv and streets.csv; and one
    new json file: repetitions.json.

    """

    def __init__(self, city_file, street_file, locality_file, number_file,
                 street_id_generator, locality_id_generator,
                 repetition_id_generator, repetitions):
        self.cities = dict()
        self.streets = dict()
        self.localities = dict()
        self.numbers = dict()
        self.repetitions = repetitions

        self.added_lines = 0

        self.city_file = city_file
        self.street_file = street_file
        self.locality_file = locality_file
        self.number_file = number_file

        self.street_id_generator = street_id_generator
        self.locality_id_generator = locality_id_generator
        self.repetition_id_generator = repetition_id_generator

    def update_dictionary(self, dictionary, key, value):
        if key not in dictionary:
            dictionary[key] = value
            return True
        return False

    def add_lon_lat(self, key, longitude, latitude):
        self.cities[key][3].append(float(longitude))
        self.cities[key][4].append(float(latitude))

    def add_id(self, dictionary, key, value_id):
        dictionary[key] = (value_id, ) + dictionary[key]

    def get_id(self, dictionary, key, value_tuple, id_gen):
        if self.update_dictionary(dictionary, key, value_tuple):
            value_id = str(next(id_gen))
            self.add_id(dictionary, key, value_id)
            return value_id
        return dictionary[key][0]

    def update(self, processed_line):
        numero = processed_line.get_numero()
        repetition = processed_line.get_repetition()
        code_insee = processed_line.get_code_insee()
        code_postal = processed_line.get_code_postal()
        nom_ld = processed_line.get_nom_ld()
        nom_afnor = processed_line.get_nom_afnor()
        commune = processed_line.get_commune()
        longitude = processed_line.get_longitude()
        latitude = processed_line.get_latitude()

        city_key = (code_insee, code_postal)
        tuple_city = (code_insee, code_postal, commune, [], [])
        self.update_dictionary(self.cities, city_key, tuple_city)
        self.add_lon_lat(city_key, longitude, latitude)

        street_key = (code_insee, code_postal, nom_afnor)
        street_tuple = (code_insee, code_postal, nom_afnor)
        street_id = self.get_id(self.streets, street_key, street_tuple,
                                self.street_id_generator)

        locality_key = (code_insee, code_postal, nom_ld)
        locality_tuple = (code_insee, code_postal, nom_ld)
        locality_id = self.get_id(self.localities, locality_key,
                                  locality_tuple, self.locality_id_generator)

        repetition_id = self.get_id(self.repetitions, repetition, (),
                                    self.repetition_id_generator)

        number_key = (street_id, locality_id, numero, repetition)
        number_value = (street_id, locality_id, numero, repetition_id,
                        str(geohash(float(longitude), float(latitude))))
        self.update_dictionary(self.numbers, number_key, number_value)

        self.added_lines += 1

    def write_new_lines(self, fhandle, dictionary):
        for key, value_tuple in dictionary.items():
            line = ';'.join(value_tuple)
            fhandle.write(line + '\n')

    def compute_mean_position(self):
        for key, city_tuple in self.cities.items():
            lon_mean = np.mean(city_tuple[3])
            lat_mean = np.mean(city_tuple[4])
            lon_str = str(degree_to_int(lon_mean))
            lat_str = str(degree_to_int(lat_mean))
            city_tuple = city_tuple[:3] + (lon_str, lat_str)
            self.cities[key] = city_tuple

    def print_results(self, exceptions):
        print('added %d lines' % self.added_lines)

        duplicates = self.added_lines - len(self.numbers)
        if duplicates > 0:
            print('duplicates: %d' % duplicates)

        if exceptions > 0:
            print('exceptions: %d' % exceptions)

    def finish(self, exceptions):
        self.compute_mean_position()

        self.write_new_lines(self.street_file, self.streets)
        self.write_new_lines(self.locality_file, self.localities)
        self.write_new_lines(self.number_file, self.numbers)
        self.write_new_lines(self.city_file, self.cities)

        self.print_results(exceptions)
