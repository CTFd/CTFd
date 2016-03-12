from flask import Flask, render_template, request, redirect, abort, session, jsonify, json as json_mod, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler
from flask.ext.session import Session
from sqlalchemy_utils import database_exists, create_database
import os
import sqlalchemy


def create_app(config='CTFd.config'):
    app = Flask("CTFd")
    with app.app_context():
        app.config.from_object(config)

        from CTFd.models import db, Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking

        ## sqlite database creation is relative to the script which causes issues with serve.py
        if not database_exists(app.config['SQLALCHEMY_DATABASE_URI']) and not app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
            create_database(app.config['SQLALCHEMY_DATABASE_URI'])

        db.init_app(app)
        db.create_all()

        app.db = db

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

        return app
