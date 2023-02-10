from flask_login import UserMixin
from sqlalchemy.orm import backref
from sqlalchemy.sql import func

from ordercentral import db


# Users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150))
    lastname = db.Column(db.String(150))
    company = db.Column(db.String(150))
    title = db.Column(db.String(50))
    aboutme = db.Column(db.Text)
    address = db.Column(db.String(150))
    city = db.Column(db.String(150))
    state = db.Column(db.String(2))
    postalcode = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150), unique=True)
    dob = db.Column(db.Date)
    avatar_filename = db.Column(db.Text)
    avatar_url = db.Column(db.String(250))
    twitter = db.Column(db.String(255))
    instagram = db.Column(db.String(255))
    facebook = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())

    def fullname(self):
        return self.firstname + " " + self.lastname

    def fulladdress(self):
        return self.address + " " + self.city + ", " + self.state + " " + self.postalcode

    def firstinit_lastname(self):
        return self.firstname[:1] + " " + self.lastname


class USZip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    zip = db.Column(db.String(12))
    type = db.Column(db.String(100))
    primary_city = db.Column(db.String(100))
    acceptable_cities = db.Column(db.String(100))
    state = db.Column(db.String(25))
    county = db.Column(db.String(100))
    timezone = db.Column(db.String(100))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())
