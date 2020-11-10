from flask import Flask
from flask_app import app
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


def configure_database(app: Flask):
    # base directory for database
    database_dir = os.path.abspath(os.path.dirname(__file__))

    # initialize database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(database_dir, 'db.sqlite')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # create Database instance
    db = SQLAlchemy(app)

    # create Marshmallow instance
    marshmallow = Marshmallow(app)

    return db, marshmallow


# create global database and marshmallow instances
db, marshmallow = configure_database(app)
