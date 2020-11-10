from flask import Flask
from flask_app import app
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# base directory for database
database_dir = os.path.abspath(os.path.dirname(__file__))


def configure_database(app: Flask):
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

# Objects that should be initially added when the database is created
database_init = []


# create the database if it does not exist and add all initial objects
def create_database():
    if not db or os.path.exists(os.path.join(database_dir, 'db.sqlite')):
        return
    db.create_all()
    for item in database_init:
        db.session.add(item)
    db.session.commit()
