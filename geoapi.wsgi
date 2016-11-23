import sys
import logging

logging.basicConfig(stream=sys.stderr)

from api import app as application
application.secret_key = 'qsfe19T7QSDHFS3qfsdqs!sqfd'
