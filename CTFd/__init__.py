from flask import Flask, render_template, request, redirect, abort, session, jsonify, json as json_mod, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail, Message
from logging.handlers import RotatingFileHandler
from flask.ext.session import Session
import logging
import os
import sqlalchemy

def create_app(subdomain="", username="", password=""):
    app = Flask("CTFd", static_folder="../static", template_folder="../templates")
    with app.app_context():
        app.config.from_object('CTFd.config')
        
        if subdomain:
            app.config.update(
                SQLALCHEMY_DATABASE_URI = 'mysql://'+username+':'+password+'@localhost:3306/' + subdomain + '_ctfd',
                HOST = subdomain + app.config["HOST"],
                SESSION_FILE_DIR = app.config['SESSION_FILE_DIR'] + "/" + subdomain,
                DEBUG = True
            )

        from CTFd.models import db, Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking

        db.init_app(app)
        db.create_all()

        app.db = db
        # app.setup = True

        global mail
        mail = Mail(app)

        Session(app)

        from CTFd.views import init_views
        init_views(app)
        from CTFd.errors import init_errors
        init_errors(app)
        from CTFd.challenges import init_challenges
        init_challenges(app)
        from CTFd.scoreboard import init_scoreboard
        init_scoreboard(app)
        from CTFd.auth import init_auth
        init_auth(app)
        from CTFd.admin import init_admin
        init_admin(app)
        from CTFd.utils import init_utils
        init_utils(app)

        return app


# logger_keys = logging.getLogger('keys')
# logger_logins = logging.getLogger('logins')
# logger_regs = logging.getLogger('regs')

# logger_keys.setLevel(logging.INFO)
# logger_logins.setLevel(logging.INFO)
# logger_regs.setLevel(logging.INFO)

# try:
#     parent = os.path.dirname(__file__)
# except:
#     parent = os.path.dirname(os.path.realpath(sys.argv[0]))

# key_log = RotatingFileHandler(os.path.join(parent, 'logs', 'keys.log'), maxBytes=10000)
# login_log = RotatingFileHandler(os.path.join(parent, 'logs', 'logins.log'), maxBytes=10000)
# register_log = RotatingFileHandler(os.path.join(parent, 'logs', 'registers.log'), maxBytes=10000)

# logger_keys.addHandler(key_log)
# logger_logins.addHandler(login_log)
# logger_regs.addHandler(register_log)

# logger_keys.propagate = 0
# logger_logins.propagate = 0
# logger_regs.propagate = 0
