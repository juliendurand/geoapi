# -*- coding: utf-8 -*-
"""Processing of the raw csv files.

This module declares two classes to handle the extraction of information from
the raw csv files.

Todo:
    * Transfer part of the work in FileProcessor into LineProcessor to obtain
    simetry betwenn the two classes and made them inherite from a more general
    class named Processor.

"""

from unidecode import unidecode
from utils import geohash, degree_to_int
import numpy as np
import itertools


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

    def update(self, line):
        """Update the object fields with a new line.

        Args:
            line (str): The line from a csv file.
        """
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

    def test(self):
        """Test the coherence of a line from a departement csv file.
        """
        result = self.ok
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


class FileProcessor():
    """Extract the information from a csv file and writes a new ones.

    This class allows the processing of a csv file following the format
    specified by the BAN documentation. One instance of LineProcessor is used
    to extract the information of each line that is then used to write four new
    csv files: cities.csv, locality.csv, numbers.csv and streets.csv; and one
    new json file: repetitions.json.

    For each of these files there is a dictionary that stores the information
    that will be written. The dictionary is used to avoid redundancy.

    Attributes:
        cities (dict): Dictionary to store the information about the cities
            (communes).
        streets (dict): Dictionary to store the information about the streets.
        localities (dict): Dictionary to store the information about the
            localities (lieu-dit).
        numbers (dict): Dictionary to store the information about the address
            numbers.
        repetitions (dict): Dictionary to store the information about the
            address number complements.
        added_lines (int): Number of lines read from a single input file.
        exceptions (int): NUmber of jumped lines from a single input file.
        lineProc (LineProcessor): Instance of LineProcessor class.
        street_id_gen (generator): Integer iterator used to create id for the
            streets.
        locality_id_gen (generator): Integer iterator used to create id for the
            localities.
        repetition_id_gen (generator): Integer iterator used to create id for
            the repetitions.

    """

    def __init__(self, city_file, street_file, locality_file, number_file):
        """__init__ method.

        Args:
            city_file (file object): Handler of the csv file to write
                 information about the cities. Mode 'w'.
            street_file (file object): Handler of the csv file to write
                information about the streets. Mode 'w'.
            locality_file (file object): Handler of the csv file to write
                information about the localities. Mode 'w'.
            number_file (file object): Handler of the csv file to write
                information about the numbers. Mode 'w'.

        """
        self.cities = dict()
        self.streets = dict()
        self.localities = dict()
        self.numbers = dict()
        self.repetitions = dict()

        self.added_lines = 0
        self.exceptions = 0

        self.lineProc = LineProcessor()

        self.city_file = city_file
        self.street_file = street_file
        self.locality_file = locality_file
        self.number_file = number_file

        self.street_id_gen = itertools.count()
        self.locality_id_gen = itertools.count()
        self.repetition_id_gen = itertools.count()

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

    def process(self, in_file):
        """Iterate over the input file and write new lines into csv files.

        This method iterates over the lines of the input file, uses the
        processing methods to extract information from these lines and writes
        all that information as new lines in the csv files.

        Args:
            in_file (file object): Handler of the input file. Mode 'r'.

        """
        self.cities = dict()
        self.streets = dict()
        self.localities = dict()
        self.numbers = dict()

        self.exceptions = 0
        self.added_lines = 0

        for line in in_file:
            self.lineProc.update(line)

            if not self.lineProc.test():
                self.exceptions += 1
                continue

            self.process_line()

        self.finish()

    def process_line(self):
        """Extract and divide the information of a line.

        This method is the responsible for handling with one single line of a
        csv file. It firstly extracts the information following the format
        described by the documentation of the files and then updates each of
        the class dictionaries with the right data.

        """

        numero = self.lineProc.numero
        repetition = self.lineProc.repetition
        code_insee = self.lineProc.code_insee
        code_postal = self.lineProc.code_postal
        nom_ld = self.lineProc.nom_ld
        nom_afnor = self.lineProc.nom_afnor
        commune = self.lineProc.commune
        longitude = self.lineProc.longitude
        latitude = self.lineProc.latitude

        # Updating cities dictionary
        city_key = (code_insee, code_postal)
        tuple_city = (code_insee, code_postal, commune, [], [])
        self.update_dictionary(self.cities, city_key, tuple_city)
        self.add_lon_lat(city_key, longitude, latitude)

        # Updating cities dictionary
        street_key = (code_insee, code_postal, nom_afnor)
        street_tuple = (code_insee, code_postal, nom_afnor)
        street_id = self.get_id(self.streets, street_key, street_tuple,
                                self.street_id_gen)

        # Updating localities dictionary
        locality_key = (code_insee, code_postal, nom_ld)
        locality_tuple = (code_insee, code_postal, nom_ld)
        locality_id = self.get_id(self.localities, locality_key,
                                  locality_tuple, self.locality_id_gen)

        # Updating repetitions dictionary
        repetition_id = self.get_id(self.repetitions, repetition, (),
                                    self.repetition_id_gen)

        # Updating numbers dictionary
        number_key = (street_id, locality_id, numero, repetition)
        number_value = (street_id, locality_id, numero, repetition_id,
                        str(geohash(float(longitude), float(latitude))))
        self.update_dictionary(self.numbers, number_key, number_value)

        self.added_lines += 1

    def write_new_lines(self, fhandle, dictionary):
        """Writes the tuple values from a dictionary in a file.

        This method iterates over the tuple values from a dictionary, converts
        it into a string separated by ';' and writes it in a csv file.

        Args:
            fhaldle (file object): Handler of the input file. Mode 'w'.
            dictionary (dict): Dictionary with tuples as values.

        """
        for key, value_tuple in dictionary.items():
            line = ';'.join(value_tuple)
            fhandle.write(line + '\n')

    def compute_mean_position(self):
        """Update the values stored in self.cities

        This method will modify the self.cities dictionary, changing the lists
        of longitude and latitude into their mean. This process is useful, to
        have a meaningful value of longitude and latitude associated to a
        city/commune.

        """
        for key, city_tuple in self.cities.items():
            lon_mean = np.mean(city_tuple[3])
            lat_mean = np.mean(city_tuple[4])
            lon_str = str(degree_to_int(lon_mean))
            lat_str = str(degree_to_int(lat_mean))
            city_tuple = city_tuple[:3] + (lon_str, lat_str)
            self.cities[key] = city_tuple

    def print_results(self):
        print('added %d lines' % self.added_lines)

        duplicates = self.added_lines - len(self.numbers)
        if duplicates > 0:
            print('duplicates: %d' % duplicates)

        if self.exceptions > 0:
            print('exceptions: %d' % self.exceptions)

    def finish(self):
        self.compute_mean_position()

        self.write_new_lines(self.street_file, self.streets)
        self.write_new_lines(self.locality_file, self.localities)
        self.write_new_lines(self.number_file, self.numbers)
        self.write_new_lines(self.city_file, self.cities)

        self.print_results()
