# 3rd-party packages
from flask import Flask, render_template, request, redirect, url_for
from flask_mongoengine import MongoEngine
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
    login_required,
)
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
from flask_talisman import Talisman
# stdlib
from datetime import datetime
import os

# local
from .client import DogClient


db = MongoEngine()
login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return None

bcrypt = Bcrypt()
dog_client = DogClient()

from flask_app.users.routes import users
from flask_app.dogs.routes import dogs


def page_not_found(e):
    return render_template("404.html"), 404


def create_app(test_config=None):
    app = Flask(__name__)

    app.config.from_pyfile("config.py", silent=False)
    if test_config is not None:
        app.config.update(test_config)
    app.config["MONGODB_HOST"] = os.getenv("MONGODB_HOST")
    db.init_app(app)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(users)
    app.register_blueprint(dogs)
    app.register_error_handler(404, page_not_found)
    inline = '\'unsafe-inline\''
    login_manager.login_view = "users.login"
    csp = {
        'default-src': ['\'self\'', 'https://dog.ceo/api'],
        'img-src': ['*','\'self\'', 'data:'],
        'style-src': ['https://stackpath.bootstrapcdn.com/bootstrap/','\'self\'','*.plot.ly/','https://js.stripe.com', inline],
        'script-src': [inline,'\'unsafe-eval\'','https://stackpath.bootstrapcdn.com/bootstrap/', 'https://code.jquery.com/', 'https://cdnjs.cloudflare.com/ajax/libs/popper.js/', 'https://cdn.jsdelivr.net/npm/popper.js@1.16.0/dist/umd/popper.min.js','\'self\'','https://cdn.plot.ly/plotly-latest.min.js','*.plot.ly', 'https://cdn.plot.ly', 'https://js.stripe.com'],
        'media-src': ['https://dog.ceo/api','https://plot.ly/','https://cdn.plot.ly/plotly-gl2d-latest.min.js'],
    }
    Talisman(app, content_security_policy=csp)
    return app
