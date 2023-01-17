from bazaar import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import datetime, os
from sqlalchemy.orm import backref, relationship
from sqlalchemy import ForeignKey


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


class MasterList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_name = db.Column(db.String(150))
    january = db.Column(db.Boolean, default=False)
    february = db.Column(db.Boolean, default=False)
    march = db.Column(db.Boolean, default=False)
    april = db.Column(db.Boolean, default=False)
    may = db.Column(db.Boolean, default=False)
    june = db.Column(db.Boolean, default=False)
    july = db.Column(db.Boolean, default=False)
    august = db.Column(db.Boolean, default=False)
    september = db.Column(db.Boolean, default=False)
    october = db.Column(db.Boolean, default=False)
    november = db.Column(db.Boolean, default=False)
    december = db.Column(db.Boolean, default=False)
    first = db.Column(db.Boolean, default=True)
    second = db.Column(db.Boolean, default=True)
    third = db.Column(db.Boolean, default=True)
    fourth = db.Column(db.Boolean, default=True)
    last = db.Column(db.Boolean, default=True)
    friday = db.Column(db.Boolean, default=False)
    saturday = db.Column(db.Boolean, default=False)
    sunday = db.Column(db.Boolean, default=False)
    monday = db.Column(db.Boolean, default=False)
    tuesday = db.Column(db.Boolean, default=False)
    wednesday = db.Column(db.Boolean, default=False)
    thursday = db.Column(db.Boolean, default=False)
    updated = db.Column(db.Date)
    imagesrc = db.Column(db.Text)
    attendance = db.Column(db.Integer)
    exibitors = db.Column(db.Integer)
    website = db.Column(db.Text)
    dates_text = db.Column(db.Text)
    type_bazaar = db.Column(db.Boolean, default=False)
    type_holiday = db.Column(db.Boolean, default=False)
    type_art = db.Column(db.Boolean, default=False)
    type_festival = db.Column(db.Boolean, default=False)
    type_flea = db.Column(db.Boolean, default=False)
    type_health = db.Column(db.Boolean, default=False)
    type_market = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    venuefk = db.Column(db.Integer, db.ForeignKey('venue.id'))
    promoterfk = db.Column(db.Integer, db.ForeignKey('promoter.id'))

    # Relationships
    venue = db.relationship("Venue", backref=backref("venue", uselist=False))
    promoter = db.relationship("Promoter", backref=backref("promoter", uselist=False))
    notes = db.relationship("Notes", backref=backref("notes", uselist=False))


class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zipcode = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(255))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Relationships
    venue_event = db.relationship("MasterList", backref=backref("masterlist", uselist=False))


class Promoter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(50))
    zipcode = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    website = db.Column(db.String(255))
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Relationships
    people = db.relationship("People", backref=backref("promoter_people", uselist=False))


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    title = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    email = db.Column(db.String(255))

    # Foreign Key
    promoterfk = db.Column(db.Integer, db.ForeignKey('promoter.id'))
    venuefk = db.Column(db.Integer, db.ForeignKey('venue.id'))

    # Relationships
    venue = db.relationship("Venue", backref=backref("people_venue", uselist=False))
    promoter = db.relationship("Promoter", backref=backref("people_promoter", uselist=False))


class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.Text)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    masterlistid = db.Column(db.Integer, db.ForeignKey('master_list.id'))
