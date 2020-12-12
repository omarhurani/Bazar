from flask import Flask
from os import environ

# Flask application instance
app = Flask(__name__)

# Get addresses of front end and order servers from the environment variables
ORDER_ADDRESS = environ.get('ORDER_ADDRESS')
FRONT_END_ADDRESS = environ.get('FRONT_END_ADDRESS')
CATALOG_ADDRESSES = environ.get('CATALOG_ADDRESSES')
if CATALOG_ADDRESSES is None or CATALOG_ADDRESSES.strip() == '':
    CATALOG_ADDRESSES = []
else:
    CATALOG_ADDRESSES = CATALOG_ADDRESSES.split('|')


# Get the flask environment settings from the environment variables
app.config['FLASK_ENV'] = environ.get('FLASK_ENV')
app.config['FLASK_DEBUG'] = bool(environ.get('FLASK_DEBUG'))


# Get the application port from the environment variables
port = int(environ.get('FLASK_PORT'))
