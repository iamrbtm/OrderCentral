from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect, url_for, send_file
)
from flask_login import login_required
from flask_mail import Message
from ordercentral.utilities import *
from ordercentral.models import *
from ordercentral import db

email = Blueprint("email", __name__, url_prefix='/email')


@email.route("/confirmation")
@login_required
def confirmation():
    record = db.session.query(Orders).filter(Orders.id == 1).first()
    return render_template('emails/confirmation.html', record=record)
