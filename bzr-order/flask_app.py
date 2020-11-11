from flask import Flask
from os import environ

app = Flask(__name__)

CATALOG_ADDRESS = environ.get('CATALOG_ADDRESS')
FRONT_END_ADDRESS = environ.get('FRONT_END_ADDRESS')


app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
app.config['FLASK_DEBUG'] = bool(environ.get('FLASK_DEBUG'))

port = int(environ.get('FLASK_PORT'))
