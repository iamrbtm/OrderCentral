from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, ALL
from dotenv import load_dotenv
from flask_mail import Mail

load_dotenv()

db = SQLAlchemy()
booking = UploadSet("booking", ALL)
uploads = UploadSet("uploads", ALL)
mail = Mail()


def create_app():
    global booking
    app = Flask(__name__)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Flask-Uploads & Static
    app.config["UPLOADED_UPLOADS_DEST"] = "bazaar/static/uploads"
    app.config["UPLOADED_BOOKING_DEST"] = "bazaar/templates/booking/uploads"
    configure_uploads(app, uploads)
    configure_uploads(app, booking)

    app._static_folder = "static"

    # Secrete Key
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    # Database Setup
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'testing.db')
    db_uri = 'sqlite:///{}'.format(db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TIMEZONE'] = 'local'
    db.init_app(app)

    # Migration for Database
    Migrate(app, db)

    # Mail Setup
    config_mail(app)

    # Blueprints
    from bazaar.auth import auth
    from bazaar.templates.base.base import base
    from bazaar.templates.masterlist.masterlist import ml
    from bazaar.templates.booking.booking import booking

    app.register_blueprint(base)
    app.register_blueprint(auth)
    app.register_blueprint(ml)
    app.register_blueprint(booking)

    with app.app_context():
        db.create_all()

    from bazaar.models import User
    # User Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def config_mail(app):
    stopper = True
    errorlist = []
    if os.environ.get("MAIL_USE") == "True":
        fields = [
            "MAIL_SERVER",
            "MAIL_PORT",
            "MAIL_USERNAME",
            "MAIL_PASSWORD",
            "MAIL_USE_TLS",
            "MAIL_USE_SSL",
            "MAIL_DEFAULT_SENDER",
        ]

        for field in fields:
            if field not in os.environ:
                msg = f"{field} not configured"
                errorlist.append(msg)
                stopper = False
            if os.environ.get(field) == "":
                msg = f"value for {field} not set"
                errorlist.append(msg)
                stopper = False
            if stopper:
                app.config[field] = os.environ.get(field)

        if stopper:
            mail.init_app(app)
        else:
            print("DID NOT INIT MAIL... ")
            print(errorlist)
