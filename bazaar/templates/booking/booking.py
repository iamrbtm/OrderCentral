from flask import (
    Blueprint,
    render_template, request
)
from flask_login import login_required, current_user
from bazaar.models import *
from bazaar import db

booking = Blueprint("booking", __name__, url_prefix="/booking")


@booking.route("/<id>")
@login_required
def home(id):
    record = db.session.query(MasterList).filter(MasterList.id == id).first()
    content = {"user": User, "record": record}
    return render_template("booking/booking_main.html", **content)
