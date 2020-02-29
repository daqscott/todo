#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

from flask import Flask
from celery import Celery
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_admin.contrib.sqla import ModelView

# from api import api
# from database import migrate
from model import User, Task, Project, WorkDay, TodoList

config_variable_name = 'FLASK_CONFIG_PATH'
default_config_path = os.path.join(os.path.dirname(__file__), 'config/local.py')
os.environ.setdefault(config_variable_name, default_config_path)


def create_app(config_file=None, settings_override=None):
    app = Flask(__name__)
    sess = Session()

    # app.config["SESSION_TYPE"] = "filesystem"
    # app.config["SECRET_KEY"] = "fuck_off_and_die_lksjdflkjsdf0982w34098324"

    if config_file:
        app.config.from_pyfile(config_file)
    else:
        app.config.from_envvar(config_variable_name)

    if settings_override:
        app.config.update(settings_override)

    sess.init_app(app)
    db = SQLAlchemy(app)
    db.init_app(app)
    with app.app_context():
        db.create_all()
    s = db.session

    app.config["FLASK_ADMIN_SWATCH"] = "cerulean"
    admin = Admin(app, name="foo", template_mode="bootstrap3")
    admin.add_view(ModelView(Task, s))
    admin.add_view(ModelView(User, s))
    admin.add_view(ModelView(Project, s))
    admin.add_view(ModelView(WorkDay, s))
    admin.add_view(ModelView(TodoList, s))

    return app


def create_celery_app(app=None):
    app = app or create_app()
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


def main():
    app = create_app()
    app.run(host="0.0.0.0")


if __name__ == "__main__":
    main()
else:
    # We want to import these objects in other places, for convenience initialize them
    app = create_app()
    db = SQLAlchemy(app)
    with app.app_context():
        db.create_all()
