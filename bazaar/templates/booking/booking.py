import os
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
    content = {"user": User, "record": record, "files": filedic, "persons": persons}
    return render_template("booking/booking_main.html", **content)


@booking.route("/<id>/adddocument", methods=["GET", "POST"])
@login_required
def adddoc(id):
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
