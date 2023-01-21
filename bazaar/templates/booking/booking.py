import os
import re

from sqlalchemy import inspect, or_
import humanize
from flask import (
    Blueprint,
    render_template, request, redirect, url_for, send_file
)
from flask_login import login_required

from bazaar import db
from bazaar.models import *

booking = Blueprint("booking", __name__, url_prefix="/booking")


def check_make_dir(id):
    path = "bazaar/templates/booking/uploads/" + id
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    return path


@booking.route("/<id>")
@login_required
def home(id):
    record = db.session.query(MasterList).filter(MasterList.id == id).first()
    path = check_make_dir(id)
    files = os.listdir(path)
    filedic = {}
    i = 0
    for file in files:
        filedic[i] = {}
        filedic[i]['file'] = file
        filedic[i]['filetype'] = os.path.splitext(os.path.join(path, file))[1]
        filedic[i]['size'] = humanize.naturalsize(os.path.getsize(os.path.join(path, file)))
        filedic[i]['created'] = datetime.datetime.fromtimestamp(os.path.getctime(os.path.join(path, file))).strftime(
            '%m/%d/%Y %H:%M %p')
        filedic[i]['editlink'] = url_for('booking.file_view', id=id, filename=file)
        filedic[i]['deletelink'] = url_for('booking.file_delete', id=id, filename=file)
        i += 1

    persons = db.session.query(People).filter(People.promoterfk == id).all()
    booking = db.session.query(Booking).filter(Booking.eventid == id).first()
    notes = db.session.query(Notes).filter(or_(Notes.masterlistid == id, Notes.bookingid == booking.id)).all()

    content = {"user": User, "record": record, "files": filedic,
               "persons": persons, "booking": booking, "notes": notes}
    return render_template("booking/booking_main.html", **content)


@booking.route("/<id>/adddocument", methods=["GET", "POST"])
@login_required
def file_add(id):
    path = check_make_dir(id)

    if request.method == "POST":
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            fullpath = os.path.join(path, uploaded_file.filename)
            uploaded_file.save(fullpath)

    return redirect(url_for('booking.home', id=id))


@booking.route("/<id>/<filename>/deletefile")
@login_required
def file_delete(id, filename):
    path = check_make_dir(id)
    os.remove(os.path.join(path, filename))
    return redirect(url_for('booking.home', id=id))


@booking.route("/<id>/<filename>/viewfile")
@login_required
def file_view(id, filename):
    path = check_make_dir(id)
    return send_file(os.path.join("templates", "booking", "uploads", id, filename))


@booking.route("/<bookingid>/<eventid>/bookingedit", methods=['POST'])
@login_required
def booking_edit(bookingid, eventid):
    booking = db.session.query(Booking).filter(Booking.id == bookingid).first()
    if request.method == "POST":
        attr_names = [c_attr.key for c_attr in inspect(Booking).mapper.column_attrs]
        data = request.form.to_dict()

        date_pattern = "^[0-9]{4}\\-[0-9]{1,2}\\-[0-9]{1,2}$"
        time_pattern = "^[0-2][0-3]:[0-5][0-9]:[0-5][0-9]$"
        for name in attr_names:
            if name[:3] == "cl_":
                if name in data:
                    setattr(booking, name, True)
                else:
                    setattr(booking, name, False)
            else:
                if name in data:
                    if name != "id" and name != "eventid":
                        if re.match(date_pattern, data[name]) != None:
                            setattr(booking, name, datetime.datetime.strptime(data[name], "%Y-%m-%d"))
                        elif re.match(time_pattern, data[name]) != None:
                            setattr(booking, name, datetime.datetime.strptime(data[name], "%H:%M:%S"))
                        elif data[name] == 'on':
                            setattr(booking, name, True)
                        else:
                            if data[name] == '':
                                setattr(booking, name, None)
                            else:
                                setattr(booking, name, data[name])
            db.session.commit()
    return redirect(url_for('booking.home', id=eventid))


@booking.route("/bookingadd/<id>")
@login_required
def booking_add(id):
    booking = db.session.query(Booking).filter(Booking.eventid == id).all()
    if len(booking) == 0:
        newbooking = Booking(
            eventid=id
        )
        db.session.add(newbooking)
        db.session.commit()

    return redirect(url_for('booking.home', id=id))
