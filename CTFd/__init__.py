from flask import Flask, render_template, request, redirect, abort, session, jsonify, json as json_mod, url_for
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from flask_session import Session
from sqlalchemy_utils import database_exists, create_database
from jinja2 import FileSystemLoader, TemplateNotFound
from utils import get_config, set_config, cache
import os
import sqlalchemy
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError


class ThemeLoader(FileSystemLoader):
    def get_source(self, environment, template):
        if template.startswith('admin/'):
            return super(ThemeLoader, self).get_source(environment, template)
        theme = get_config('ctf_theme')
        template = "/".join([theme, template])
        return super(ThemeLoader, self).get_source(environment, template)


def create_app(config='CTFd.config'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        app.jinja_loader = ThemeLoader(os.path.join(app.root_path, app.template_folder), followlinks=True)

        from CTFd.models import db, Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking

        url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
        if url.drivername == 'postgres':
            url.drivername = 'postgresql'

        db.init_app(app)

        try:
            if not (url.drivername.startswith('sqlite') or database_exists(url)):
                create_database(url)
            db.create_all()
        except OperationalError:
            db.create_all()
        else:
            db.create_all()

        app.db = db

        cache.init_app(app)
        app.cache = cache

        if not get_config('ctf_theme'):
            set_config('ctf_theme', 'original')

        #Session(app)

        from CTFd.views import views
        from CTFd.challenges import challenges
        from CTFd.scoreboard import scoreboard
        from CTFd.auth import auth
        from CTFd.admin import admin
        from CTFd.utils import init_utils, init_errors, init_logs

        init_utils(app)
        init_errors(app)
        init_logs(app)

        app.register_blueprint(views)
        app.register_blueprint(challenges)
        app.register_blueprint(scoreboard)
        app.register_blueprint(auth)
        app.register_blueprint(admin)

        from CTFd.plugins import init_plugins

        init_plugins(app)

        return app
