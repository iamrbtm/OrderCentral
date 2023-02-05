from flask_login import UserMixin
from sqlalchemy.orm import backref
from sqlalchemy.sql import func

from bazaar import db


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


# noinspection SpellCheckingInspection
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
    active = db.Column(db.Boolean, default=True)
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
    venue_event = db.relationship("MasterList", backref=backref("masterlist_home", uselist=False))


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
    bookingid = db.Column(db.Integer, db.ForeignKey('booking.id'))


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kd_appopen_new = db.Column(db.Date)
    kd_appopen_return = db.Column(db.Date)
    kd_appdeadline_new = db.Column(db.Date)
    kd_appdeadline_return = db.Column(db.Date)
    cl_appsubmission = db.Column(db.Boolean, default=False)
    cl_interested = db.Column(db.Boolean, default=True)
    cl_appapproved = db.Column(db.Boolean, default=False)
    cl_feepaid = db.Column(db.Boolean, default=False)
    cl_electrequest = db.Column(db.Boolean, default=False)
    cl_sendproductpic = db.Column(db.Boolean, default=False)
    cl_sendlogo = db.Column(db.Boolean, default=False)
    cl_sendbio = db.Column(db.Boolean, default=False)
    info_wifipassword = db.Column(db.String(100))
    info_datestart = db.Column(db.Date)
    info_dateend = db.Column(db.Date)
    info_timestart = db.Column(db.Time)
    info_timeend = db.Column(db.Time)
    info_loadindatetime = db.Column(db.DateTime)
    info_loadoutdatetime = db.Column(db.DateTime)
    info_boothfee = db.Column(db.Float)
    info_whatfeeincludes = db.Column(db.Text)
    info_boothlocation = db.Column(db.String(100))
    cl_wifiavailable = db.Column(db.Boolean, default=False)
    cl_foodavailable = db.Column(db.Boolean, default=False)
    info_foodpurchase = db.Column(db.String(100))
    days_remaining = db.Column(db.Integer)
    next_touch = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True)
    date_created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    eventid = db.Column(db.Integer, db.ForeignKey('master_list.id'))

    # Relationships
    notes = db.relationship("Notes", backref=backref("booking_notes", uselist=False))
    event = db.relationship("MasterList", backref=backref("booking_event", uselist=False))


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
