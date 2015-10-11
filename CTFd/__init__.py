from flask import Flask, render_template, request, redirect, abort, session, jsonify, json as json_mod, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail, Message
from logging.handlers import RotatingFileHandler
from flask.ext.session import Session
import os
import sqlalchemy


def create_app(config='CTFd.config'):
    app = Flask("CTFd")
    with app.app_context():
        app.config.from_object(config)

        from CTFd.models import db, Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking

        db.init_app(app)
        db.create_all()

        app.db = db

        global mail
        mail = Mail(app)

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
