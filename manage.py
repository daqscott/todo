#!/usr/bin/env python

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import MigrateCommand
from flask_script import Manager, Command

from app import create_app
from tasks import run_celery
from tests.command import PytestCommand

app = create_app()
db = SQLAlchemy(app)

manager = Manager(create_app)
manager.add_option('-c', '--config', dest='config_file', required=False)
manager.add_command('db', MigrateCommand)
manager.add_command('test', PytestCommand)
manager.add_command('runcelery', Command(run_celery))

if __name__ == '__main__':
    manager.run()
