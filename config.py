import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Default
    SECRET_KEY = os.getenv('SECRET_KEY')

class ProductionConfig(Config):
    # Debug
    DEBUG = False

class DevelopmentConfig(Config):
    # Debug
    DEBUG = True
