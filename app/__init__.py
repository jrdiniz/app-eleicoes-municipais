# Flask
from flask import Flask

# Extensions
from app.extensions import configuration
from app.extensions import database
from app.extensions import command

# Blueprints
from app.blueprints import webui

# Celery
from celery import Celery
from celery import Task

def create_app() -> Flask:
    app = Flask(__name__)

    # Initialize Extensions
    configuration.init_app(app)
    database.init_app(app)
    command.init_app(app)
    
    # Initialize Celery
    app.config.from_mapping(
        CELERY=dict(
            broker_url="redis://localhost",
            result_backend="redis://localhost",
            task_ignore_result=True,
        ),
    )
    app.config.from_prefixed_env()
    celery_init_app(app)
    
    # Initialize Blueprints
    webui.init_app(app)
    
    return app

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    configuration.init_app(app)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.conf.task_queues = {
        'default': {'exchange': 'default', 'binding_key': 'default'},
        'eleicoes_queue': {'exchange': 'eleicoes_queue', 'binding_key': 'eleicoes_queue'}
    }
    celery_app.conf.task_routes = {
        'app.blueprints.tasks.*': {'queue': 'eleicoes_queue'}
    }
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    celery_app.autodiscover_tasks(['app.blueprints.tasks'])
    return celery_app