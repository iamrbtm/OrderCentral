import asyncio
import os
import aiosqlite
from flask import (
    Blueprint,
    render_template,
    request,
    redirect, url_for, send_file
)
from flask_login import login_required, current_user
from sqlalchemy import and_
from datetime import datetime, timedelta

from ordercentral.models import *
from ordercentral import db

base = Blueprint("base", __name__)


@base.app_template_filter()
def format_date(item, fmt="%m/%d/%Y"):
    return item.strftime(fmt)


@base.route("/")
@base.route("/home")
@login_required
def home():
    content = {"user": User,
               }
    return render_template("base/dashboard.html", **content)


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
