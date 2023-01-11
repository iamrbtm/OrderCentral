from flask import (
    Blueprint,
    render_template, request
)
from flask_login import login_required, current_user
from bazaar.models import *
from bazaar import db

base = Blueprint("base", __name__)


@base.route("/")
@base.route("/home")
@login_required
def home():
    return render_template("base/base.html", user=User)


@base.route('/importfile')
def importfile():
    from bazaar.importfile import main
    main()
    return render_template("base/base.html", user=User)


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

# @base.route("/profile", methods=["GET", "POST"])
# @login_required
# def profile():
#     usr = db.session.query(User).filter(User.id == flask_login.current_user.id).first()
#
#     if request.method == "POST":
#         if request.form.get("where") == "picture":
#             filename = avatar.save(request.files['picture'])
#             path = '/app/img/avatars'
#
#             # Save to db
#             current_user.avatar_filename = filename
#             current_user.avatar_url = os.path.join(path,filename)
#
#         elif request.form.get("where") == "contact":
#             current_user.firstname = request.form.get("firstname")
#             current_user.lastname = request.form.get("lastname")
#             current_user.address = request.form.get("address")
#             current_user.city = request.form.get("city")
#             current_user.state = request.form.get("state")
#             current_user.postalcode = request.form.get("postalcode")
#             current_user.phone = format_tel(request.form.get("phone"))
#             current_user.dob = request.form.get("dob")
#
#         elif request.form.get("where") == "user":
#             current_user.username = request.form.get('username')
#             current_user.email = request.form.get('email')
#
#         db.session.commit()
#         flash("Information Saved")
#         return redirect(url_for("base.profile"))
#
#     states = db.session.query(States).all()
#     return render_template("app/base/profile.html", user=User, states=states)
