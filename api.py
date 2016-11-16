import importlib
import json

from flask import Flask

import main


db = main.load_db()

app = Flask(__name__)


@app.route('/search')
def search():
    return 'ok'


@app.route('/reload')
def reload():
    importlib.reload(main)
    return 'ok'

if __name__ == '__main__':
    app.run()
