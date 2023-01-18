from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from dotenv import load_dotenv
from flask_mail import Mail

load_dotenv()

db = SQLAlchemy()
photos = UploadSet("photos", IMAGES)
uploads = UploadSet("uploads", ALL)
mail = Mail()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Flask-Uploads & Static
    app.config["UPLOADED_PHOTOS_DEST"] = "bazaar/static/images"
    app.config["UPLOADED_UPLOADS_DEST"] = "bazaar/static/uploads"
    configure_uploads(app, photos)
    configure_uploads(app, uploads)

    app._static_folder = "static"

    # Secrete Key
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    # Database Setup
    app.config[
        "SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://onlymyli_rbtm2006:Braces4me##@192.96.200.111/onlymyli_bazaar?charset=utf8mb4"
    # db_path = os.path.join(os.path.dirname(__file__), 'database', 'testing.db')
    # db_uri = 'sqlite:///{}'.format(db_path)
    # app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
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

    from bazaar.models import User

    with app.app_context():
        db.create_all()

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
