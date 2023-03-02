from flask_login import UserMixin
from sqlalchemy.orm import backref
from sqlalchemy.sql import func

from ordercentral import db
import json


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


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ordernum = db.Column(db.Integer)
    total = db.Column(db.Float)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    personfk = db.Column(db.Integer, db.ForeignKey('people.id'))

    # Relationships
    person = db.relationship("People", backref=backref("people", uselist=False))


class OrderLineItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    saleprice = db.Column(db.Float)
    data = db.Column(db.JSON)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    orderfk = db.Column(db.Integer, db.ForeignKey('orders.id'))
    productfk = db.Column(db.Integer, db.ForeignKey('product.id'))

    # Relationships
    orders = db.relationship("Orders", backref=backref("orders", uselist=False))
    products = db.relationship("Product", backref=backref("product", uselist=False))

    @property
    def json_data(self):
        return json.loads(self.data)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    display_name = db.Column(db.String(150))
    cost = db.Column(db.Float)
    qty = db.Column(db.Integer)
    event = db.Column(db.String(200))
    bookingid = db.Column(db.Integer)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100))
    lname = db.Column(db.String(100))
    mailing_address = db.Column(db.String(100))
    mailing_city = db.Column(db.String(100))
    mailing_state = db.Column(db.String(2))
    mailing_zipcode = db.Column(db.String(15))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    def full_name(self):
        return self.fname + " " + self.lname

    def one_line_address(self):
        return self.mailing_address + " " + self.mailing_city + ", " + self.mailing_state + " " + self.mailing_zipcode


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
