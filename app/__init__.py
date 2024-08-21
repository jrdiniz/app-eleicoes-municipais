# Flask
from flask import Flask

# Extensions
from app.extensions import configurations

# Blueprints
from app.blueprints import webui


def create_app():
    app = Flask(__name__)

    # Initialize Extensions
    configurations.init_app(app)

    # Initialize Blueprints
    webui.init_app(app)

    return app
