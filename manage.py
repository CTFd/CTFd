from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from CTFd import create_app
from CTFd.utils import get_config as get_config_util, set_config as set_config_util
from CTFd.models import *

app = create_app()

manager = Manager(app)
manager.add_command("db", MigrateCommand)


@manager.command
def get_config(key):
    with app.app_context():
        print(get_config_util(key))


@manager.command
def set_config(key, value):
    with app.app_context():
        print(set_config_util(key, value).value)


if __name__ == "__main__":
    manager.run()
