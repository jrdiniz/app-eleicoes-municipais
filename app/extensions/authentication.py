import datetime
from flask import session
from flask_login import LoginManager
from flask_login import UserMixin
from flask_login import login_user
from flask_login import logout_user
from flask_login import login_required
from flask_login import current_user

login_manager = LoginManager()


def init_app(app):
    login_manager.session_protection = "strong"
    login_manager.login_view = "webui.login"
    login_manager.refresh_view = "webui.login"
    login_manager.init_app(app)
