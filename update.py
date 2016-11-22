import os
import sys

import requests
import zipfile


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
