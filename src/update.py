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

import os

import requests
import references as ref
import zipfile

DIR = ref.DATA_DIR
BAN_DIR = ref.BAN_SUBDIR
FILE = 'ban.zip'

FILE_PATH = os.path.join(DIR, FILE)
UNZIP_PATH = os.path.join(DIR, BAN_DIR)

URL = 'https://adresse.data.gouv.fr/data/BAN_licence_gratuite_repartage.zip'


def get_ban_file():
    """
    Downloads FILE from URL and stores it in DIR. This directory is not
    required to exist before the execution of the method, and if FILE exists,
    it will be overwritten
    """
    print('retrieving ban file : %s' % URL)

    # Certifies the existence of the directory.
    if not os.path.exists(DIR):
        os.mkdir(DIR)

    # Certifies that the directory does not have FILE
    if os.path.exists(FILE_PATH):
        os.remove(FILE_PATH)

    # Downloads the content and stores it at FILE_PATH.
    with open(FILE_PATH, 'wb') as handle:
        response = requests.get(URL, stream=True)

        if not response.ok:
            raise Exception("Bad Response")

        for block in response.iter_content(1024):
            handle.write(block)

    print('download complete')


def unzip():
    """
    Uncompress FILE from DIR in the subdirectory BAN_DIR.
    """
    print('unzip ban file at : %s' % FILE_PATH)

    # Certifies the existence of the subdirectory.
    if not os.path.exists(UNZIP_PATH):
        os.mkdir(UNZIP_PATH)

    # Uncompress each file within FILE
    with zipfile.ZipFile(FILE_PATH) as zf:
        for member in zf.infolist():
            zf.extract(member, UNZIP_PATH)

    print('unzip complete')


if __name__ == '__main__':
    print('UPDATING BAN FILE')

    get_ban_file()  # Download
    unzip()  # Uncompress

    print("DONE")
