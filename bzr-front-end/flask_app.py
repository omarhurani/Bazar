from flask import Flask
from os import environ

# Flask application instance
app = Flask(__name__)

# Get addresses of catalog and order servers from the environment variables
# Addresses are split by a '|'
CATALOG_ADDRESSES = environ.get('CATALOG_ADDRESSES').split('|')
ORDER_ADDRESSES = environ.get('ORDER_ADDRESSES').split('|')


# Get the flask environment settings from the environment variables
app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
app.config['FLASK_DEBUG'] = bool(environ.get('FLASK_DEBUG'))

# Get the application port from the environment variables
port = int(environ.get('FLASK_PORT'))
