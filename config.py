import os
import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    # Default
    SECRET_KEY = os.getenv('SECRET_KEY')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class ProductionConfig(Config):
    # Debug
    DEBUG = False

    # MySQL Database
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_ADDRESS')}/{os.getenv('MYSQL_DATABASE')}?charset=utf8mb4"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 20,'max_overflow':0, 'pool_recycle': 200, 'pool_pre_ping': True}

    PLAINLY_API_KEY = '3ERTGr2Ze7H9AzDVrNqPkBM4aLR69zzT'
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = datetime.timedelta(minutes=120)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = False
    
    CELERY = {
        'broker_url': 'redis://localhost:6379/0',
        'result_backend': 'redis://localhost:6379/0',
        'task_ignore_result': True,
        'broker_connection_retry_on_startup': True,
        "beat_schedule": {
            "pegar_atualizacao": {
                "task": "app.blueprints.tasks.task_pegar_atualizacao", 
                "schedule": datetime.timedelta(minutes=15)
            },
            "pegar_video": {
                "task": "app.blueprints.tasks.task_pegar_video", 
                "schedule": datetime.timedelta(minutes=1)
            },
            "atualizar_video_state": {
                "task": "app.blueprints.tasks.task_atualizar_video_state", 
                "schedule": datetime.timedelta(minutes=1)
            },
        }
    }
    
class DevelopmentConfig(Config):
    # Debug
    DEBUG = True

    # MySQL Database
    SQLALCHEMY_DATABASE_URI = f"mysql://{os.getenv('MYSQL_USERNAME')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_ADDRESS')}/{os.getenv('MYSQL_DATABASE')}?charset=utf8mb4"
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 20,'max_overflow':0, 'pool_recycle': 200, 'pool_pre_ping': True}
    
    PLAINLY_API_KEY = '3ERTGr2Ze7H9AzDVrNqPkBM4aLR69zzT'
    
    # Flask-Login
    REMEMBER_COOKIE_DURATION = datetime.timedelta(minutes=120)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_REFRESH_EACH_REQUEST = False
    
    
    CELERY = {
        'broker_url': 'redis://localhost:6379/0',
        'result_backend': 'redis://localhost:6379/0',
        'task_ignore_result': True,
        'broker_connection_retry_on_startup': True,
        "beat_schedule": {
            "pegar_atualizacao": {
                "task": "app.blueprints.tasks.task_pegar_atualizacao", 
                "schedule": datetime.timedelta(minutes=2),
                "options":{'queue': 'eleicoes_queue'}
            },
            "atualizar_video_state": {
                "task": "app.blueprints.tasks.task_atualizar_video_state", 
                "schedule": datetime.timedelta(minutes=1),
                "options":{'queue': 'eleicoes_queue'}
            },
        }
    }
    