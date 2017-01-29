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
import sys

import requests
import zipfile

from src.index import index


BAN_FILE_PATH = 'data/ban.zip'


def get_ban_file(url):
    print('retrieving ban file : %s' % url)

    if not os.path.exists("data"):
        os.mkdir("data")

    if os.path.exists(BAN_FILE_PATH):
        os.remove(BAN_FILE_PATH)

    with open(BAN_FILE_PATH, 'wb') as handle:
        response = requests.get(url, stream=True)

        if not response.ok:
            raise Exception("Bad Response")

        for block in response.iter_content(1024):
            handle.write(block)


def unzip(source_filename, dest_dir):
    print('unzip ban file %s' % source_filename)
    if not os.path.exists(dest_dir):
        os.mkdir(dest_dir)
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                while True:
                    drive, word = os.path.splitdrive(word)
                    head, word = os.path.split(word)
                    if not drive:
                        break
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            zf.extract(member, path)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        url = sys.argv[1]
        get_ban_file(url)
        unzip(BAN_FILE_PATH, 'data/ban/')
        index()
        print("DONE")
