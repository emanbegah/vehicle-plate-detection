from . import db
from flask_login import UserMixin


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    email = db.Column(db.String(200))
    userkey = db.Column(db.String(30))
    pin = db.Column(db.String(10000))
