from .storage import Storage
from .scheduler import Scheduler
import os
from flask import Flask
from attlasian import Attlasian
from flask_assets import Environment, Bundle
import logging


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_envvar("FLASK_CONFIG")
    gunicorn_logger = logging.getLogger("gunicorn.error")
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(gunicorn_logger.level)

    assets = Environment(app)

    Storage.register(app)
    Scheduler.register(app)
    Scheduler.start()
    Attlasian.register(app)

    scss = Bundle("scss/site.scss", filters="pyscss")
    styles = Bundle(
        "css/normalize.css",
        "css/terminal.css",
        scss,
        filters="cssmin",
        output="gen/style.css",
    )
    assets.register("styles", styles)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from . import index
    from app import jira

    app.register_blueprint(index.bp)
    app.register_blueprint(jira.bp)
    app.add_url_rule("/", endpoint="index")
    
    return app
