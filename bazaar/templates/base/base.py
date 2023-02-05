import asyncio
import os
import aiosqlite
from flask import (
    Blueprint,
    render_template,
    request,
    redirect, url_for
)
from flask_login import login_required, current_user
from sqlalchemy import and_
from datetime import datetime, timedelta

import bazaar.utilities
from bazaar.models import *
from bazaar import db

base = Blueprint("base", __name__)


@base.app_context_processor
def zipcode_qty_check():
    zipcode_count = db.session.query(func.count(USZip.id)).scalar()
    checking = zipcode_count == 0
    return dict(zipcode_count_check=checking)


@base.app_template_filter()
def format_date(item, fmt="%m/%d/%Y"):
    return item.strftime(fmt)


@base.app_context_processor
def notification_count():
    now = datetime.now()

    days_from_now = datetime.now() + timedelta(days=1)
    notcount = db.session.query(func.count(Booking.id)).filter(
        Booking.active == True,
        Booking.next_touch <= days_from_now
    ).scalar()
    if notcount == 0:
        return dict(notification_count=None)
    else:
        return dict(notification_count=notcount)


@base.app_context_processor
def notifications():
    days_from_now = datetime.now() + timedelta(days=1)
    nots = db.session.query(Booking).filter(
        Booking.active == True,
        Booking.next_touch <= days_from_now
    ).order_by(Booking.next_touch).all()
    return dict(notifications=nots)


def file_exists(file_path):
    return os.path.isfile(file_path)


@base.context_processor
def file_checker():
    file_path = 'bazaar/static/import_files/festivalnet_dot_com.csv'
    return dict(file_present=file_exists(file_path))


@base.route("/")
@base.route("/home")
@login_required
def home():
    countrec = db.session.query(func.count(MasterList.id)).scalar()

    countinterest = db.session.query(func.count(Booking.id)).filter(Booking.active == True).filter(
        and_(Booking.cl_appsubmission == False, Booking.cl_appapproved == False)).scalar()
    interests = db.session.query(Booking).filter(Booking.active == True).filter(
        and_(Booking.cl_appsubmission == False, Booking.cl_appapproved == False)).order_by(Booking.info_datestart).all()

    countapps = db.session.query(func.count(Booking.id)).filter(Booking.cl_appsubmission == True).filter(and_(
        Booking.cl_appapproved == False, Booking.cl_interested == True)).scalar()
    applications = db.session.query(Booking).filter(Booking.cl_appsubmission == True).filter(and_(
        Booking.cl_appapproved == False, Booking.cl_interested == True)).all()

    countbookings = db.session.query(func.count(Booking.id)).filter(Booking.cl_appapproved == True).scalar()
    bookings = db.session.query(Booking).filter(Booking.cl_interested == True).filter(
        and_(Booking.cl_appsubmission == True, Booking.cl_appapproved == True)).all()

    countpay = db.session.query(func.count(Booking.id)).filter(Booking.cl_appapproved == True).filter(
        Booking.cl_feepaid == False).scalar()
    amountpay = db.session.query(func.sum(Booking.info_boothfee)).filter(Booking.cl_appapproved == True).filter(
        Booking.cl_feepaid == False).scalar()

    content = {"user": User,
               "countrec": countrec,
               "countinterest": countinterest,
               "interests": interests,
               "countapps": countapps,
               "applications": applications,
               "countbookings": countbookings,
               "bookings": bookings,
               "amountpay": amountpay,
               "countpay": countpay
               }
    return render_template("base/dashboard.html", **content)


@base.route('/importfile')
def importfile():
    from bazaar.importfile import main
    main()
    return redirect(url_for('base.home'))


@base.route('/importzipcodes')
def importzipcodes():
    async def import_data(asyncsql):
        # Connect to the database asynchronously
        async with aiosqlite.connect('bazaar/database/testing.db') as conn:
            c = await conn.cursor()

            # Split the insert statements into a list
            statements = asyncsql.split(';')

            # Execute the insert statements asynchronously
            for statement in statements:
                await c.execute(statement)

            # Commit the changes
            await conn.commit()

    # Read the insert statements from the file
    with open('bazaar/templates/base/USZip.sql', 'r') as file:
        sql = file.read()

    # Start the event loop and run the import process asynchronously
    asyncio.run(import_data(sql))

    return redirect(url_for('base.home'))


@base.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "POST":
        record = db.session.query(User).filter(User.id == current_user.id).first()

        data = request.form.to_dict()

        for key in data.keys():
            setattr(record, key, data[key])
            db.session.commit()

    return render_template("base/users-profile.html", user=User)


@base.route("/transfer_data", methods=["GET", "POST"])
@login_required
def transfer_data():
    from bazaar.move_bookings_to_dfp import transfer_data
    transfer_data()


@base.route("/tempfunc")
@login_required
def tempfunc():
    bazaar.utilities.tempfunc()
