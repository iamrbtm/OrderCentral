from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from flask_login import LoginManager
from flask_migrate import Migrate
from dotenv import load_dotenv
from flask_mail import Mail

load_dotenv()

db = SQLAlchemy()
mail = Mail()


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app._static_folder = "static"

    # Secrete Key
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    # Database Setup
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'ordercentral.db')
    db_uri = 'sqlite:///{}'.format(db_path)
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TIMEZONE'] = 'local'
    db.init_app(app)

    # Migration for Database
    Migrate(app, db)

    # Mail Setup
    app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER')
    app.config["MAIL_PORT"] = os.environ.get('MAIL_PORT')
    app.config["MAIL_USERNAME"] = os.environ.get('MAIL_USERNAME')
    app.config["MAIL_PASSWORD"] = os.environ.get('MAIL_PASSWORD')
    app.config["MAIL_DEFAULT_SENDER"] = os.environ.get('MAIL_DEFAULT_SENDER')
    mail.init_app(app)

    # Blueprints
    from ordercentral.auth import auth
    from ordercentral.templates.base.base import base
    from ordercentral.templates.orders.orders import order
    from ordercentral.templates.ornament1.ornament1 import orn1
    from ordercentral.templates.seed_starter.seedstart import seed
    from ordercentral.templates.emails.email import email

    app.register_blueprint(base)
    app.register_blueprint(auth)
    app.register_blueprint(order)
    app.register_blueprint(orn1)
    app.register_blueprint(seed)
    app.register_blueprint(email)

    with app.app_context():
        db.create_all()

    from ordercentral.models import User
    # User Manager
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
