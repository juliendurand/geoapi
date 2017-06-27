# -*- coding: utf-8 -*-
"""Install and update the raw data used by the API

This module creates a directory named DIR where it downloads the BASE ADRESSE
NATIONALE (BAN), an open source data of all the addresses in France offered by
the french government.

"""

import os
import zipfile
import requests

import references as ref

DIR = ref.DATA_DIR
BAN_DIR = ref.BAN_SUBDIR
FILE = ref.FILE

FILE_PATH = ref.FILE_PATH
UNZIP_PATH = ref.UNZIP_PATH

URL = ref.URL


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

    get_ban_file()
    unzip()

    print("DONE")
