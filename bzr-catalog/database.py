from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os


def configure_database(app: Flask):
    # base directory for database
    database_dir = os.path.abspath(os.path.dirname(__file__))

    # initialize database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(database_dir, 'db.sqlite')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # create Database variable
    db = SQLAlchemy(app)

    # create Marshmallow variable
    marshmallow = Marshmallow(app)

    return db, marshmallow


# Database class singelton
class Database:
    instance = None

    def __init__(self, app):
        if not Database.instance:
            db, marshmallow = configure_database(app)
            self.app = app
            self.db = db
            self.marshmallow = marshmallow
            Database.instance = self

    @classmethod
    def get_instance(cls, app=None):
        if not cls.instance:
            if app is None:
                raise RuntimeError('Instance not created and app not provided')
            else:
                cls.instance = cls(app)
        return cls.instance
