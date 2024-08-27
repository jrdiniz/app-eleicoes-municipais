import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Default
    SECRET_KEY = os.getenv('SECRET_KEY')

class ProductionConfig(Config):
    # Debug
    DEBUG = False

    # MySQL Database
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_ADDRESS')}/{os.getenv('MYSQL_DATABASE')}?charset=utf8mb4"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 20,'max_overflow':0, 'pool_recycle': 200, 'pool_pre_ping': True}

    CREATOMATE_API_KEY = "e1beb1a49ed74076ab3e0e507ee20f7e5c8d7fe2570200bffc6c00af33fa3d3f65f0dd64febb56e95c6333f3ae3f3a41"

class DevelopmentConfig(Config):
    # Debug
    DEBUG = True

    # MySQL Database
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('MYSQL_USERNAME')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_ADDRESS')}/{os.getenv('MYSQL_DATABASE')}?charset=utf8mb4"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 20,'max_overflow':0, 'pool_recycle': 200, 'pool_pre_ping': True}

    CREATOMATE_API_KEY = "e1beb1a49ed74076ab3e0e507ee20f7e5c8d7fe2570200bffc6c00af33fa3d3f65f0dd64febb56e95c6333f3ae3f3a41"