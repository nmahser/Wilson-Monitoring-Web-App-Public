from flask_login import UserMixin
from app import dbLite

class User(UserMixin, dbLite.Model):
    id = dbLite.Column(dbLite.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    username = dbLite.Column(dbLite.String(30), unique=True)
    password = dbLite.Column(dbLite.String(100))
    name = dbLite.Column(dbLite.String(1000))