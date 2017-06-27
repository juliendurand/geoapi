# -*- coding: utf-8 -*-
"""Install and update the raw data used by the API

This module creates a directory named DIR where it downloads the BASE ADRESSE
NATIONALE (BAN), an open source data of all the addresses in France offered by
the french government.

Attributes:
    DIR (string): name of the directory where the download will be located.

    BAN_DIR (string): name of the directory where the content will be
        uncompressed.

    FILE (string): name of the file downloaded.

    FILE_PATH (string): path to find the downloaded content.

    UNZIP_PATH (string): path to the unzip data.

    URL (string): location of the web data.

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
    """Downloads FILE from URL and stores it in DIR.

    Acces web content from URL and stores it in DIR with the name of FILE.
    This directory is not required to exist before the execution of the method
    and if FILE exists, it will be overwritten.
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
    """Unzip FILE from DIR in the subdirectory BAN_DIR.

    Unzip the content of FILE, donwloaded after the execution of get_ban_file,
    in BAN_DIR. This directory is not required to exist before the execution of
    the method.
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
