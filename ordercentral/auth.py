from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from ordercentral import db
from ordercentral.models import User

auth = Blueprint("auth", __name__)


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('base.home'))
            else:
                flash("Password is incorrect.", category="error")
        else:
            flash("Email does not exist.", category="error")

    return render_template("base/login.html", user=User)


@auth.route("/sign-up", methods=["GET", "POST"])
def sign_up():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        fname = request.form.get("fname")
        lname = request.form.get("lname")

        email_exists = User.query.filter_by(email=email).first()
        username_exists = User.query.filter_by(username=username).first()

        if email_exists:
            flash("Email is already in use.", category="error")
        elif username_exists:
            flash("Username is already in use.", category="error")
        elif password1 != password2:
            flash("Password don't match!", category="error")
        elif len(username) < 2:
            flash("Username is too short.", category="error")
        elif len(password1) < 6:
            flash("Password is too short.", category="error")
        elif len(email) < 4:
            flash("Email is invalid.", category="error")
        else:
            printing_user = User(
                email=email,
                username=username,
                firstname=fname,
                lastname=lname,
                password=generate_password_hash(password1, method="sha256"),
                avatar_filename="placeholder.png",
            )
            db.session.add(printing_user)
            db.session.commit()
            login_user(printing_user, remember=True)
            flash("User created!")
            return render_template("base/base.html")

    return render_template("base/signup.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
