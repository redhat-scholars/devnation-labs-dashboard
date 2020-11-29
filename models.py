import datetime
from flask_login import UserMixin

from app import db



class Cluster(db.Model):
    id = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    event_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    name = db.Column(db.String(50), unique=True, nullable=False)
    geo = db.Column(db.String(4), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), unique=True, nullable=False)
    login_url = db.Column(db.String(2500), nullable=False)
    workshop_url = db.Column(db.String(2500), nullable=False)
    assigned = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return "<ID: {}>".format(self.id)


class User(db.Model):
    email = db.Column(db.String(100), unique=True, nullable=False, primary_key=True)
    event_date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    name = db.Column(db.String(100), nullable=False)
    geo = db.Column(db.String(4), nullable=False)
    location = db.Column(db.String(300), nullable=True)
    company = db.Column(db.String(200), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    job_role = db.Column(db.String(300), nullable=True)

    def __repr__(self):
        return "<Email: {}>".format(self.email)

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100))

    def __repr__(self):
        return "<Email: {}>".format(self.email)