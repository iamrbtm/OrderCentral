import os
import humanize
from flask import (
    Blueprint,
    render_template, request, redirect, url_for
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
        filedic[i]['editlink'] = None
        filedic[i]['deletelink'] = None
        i += 1

    content = {"user": User, "record": record, "files": filedic}
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
