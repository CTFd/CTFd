from flask import request, session, redirect, url_for, abort, render_template
from werkzeug.wsgi import DispatcherMiddleware
from CTFd.models import db, Tracking

from CTFd.utils import markdown, get_config
from CTFd.utils.dates import unix_time_millis, unix_time, isoformat

from CTFd.utils import config
from CTFd.utils.config import can_send_mail, ctf_logo, ctf_name, ctf_theme
from CTFd.utils.config.pages import get_pages
from CTFd.utils.events import EventManager, RedisEventManager
from CTFd.utils.plugins import (
    get_registered_stylesheets,
    get_registered_scripts,
    get_configurable_plugins,
    get_registered_admin_scripts,
    get_registered_admin_stylesheets,
)

from CTFd.utils.countries import get_countries, lookup_country_code
from CTFd.utils.user import authed, get_ip, get_current_user, get_current_team
from CTFd.utils.modes import generate_account_url
from CTFd.utils.config import is_setup
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.auth import logout_user

from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
    registration_visible,
    scores_visible,
)

from sqlalchemy.exc import InvalidRequestError, IntegrityError

import datetime
import logging
import os
import sys


def init_template_filters(app):
    app.jinja_env.filters["markdown"] = markdown
    app.jinja_env.filters["unix_time"] = unix_time
    app.jinja_env.filters["unix_time_millis"] = unix_time_millis
    app.jinja_env.filters["isoformat"] = isoformat


def init_template_globals(app):
    app.jinja_env.globals.update(config=config)
    app.jinja_env.globals.update(get_pages=get_pages)
    app.jinja_env.globals.update(can_send_mail=can_send_mail)
    app.jinja_env.globals.update(get_ctf_name=ctf_name)
    app.jinja_env.globals.update(get_ctf_logo=ctf_logo)
    app.jinja_env.globals.update(get_ctf_theme=ctf_theme)
    app.jinja_env.globals.update(get_configurable_plugins=get_configurable_plugins)
    app.jinja_env.globals.update(get_registered_scripts=get_registered_scripts)
    app.jinja_env.globals.update(get_registered_stylesheets=get_registered_stylesheets)
    app.jinja_env.globals.update(
        get_registered_admin_scripts=get_registered_admin_scripts
    )
    app.jinja_env.globals.update(
        get_registered_admin_stylesheets=get_registered_admin_stylesheets
    )
    app.jinja_env.globals.update(get_config=get_config)
    app.jinja_env.globals.update(generate_account_url=generate_account_url)
    app.jinja_env.globals.update(get_countries=get_countries)
    app.jinja_env.globals.update(lookup_country_code=lookup_country_code)
    app.jinja_env.globals.update(accounts_visible=accounts_visible)
    app.jinja_env.globals.update(challenges_visible=challenges_visible)
    app.jinja_env.globals.update(registration_visible=registration_visible)
    app.jinja_env.globals.update(scores_visible=scores_visible)


def init_logs(app):
    logger_submissions = logging.getLogger("submissions")
    logger_logins = logging.getLogger("logins")
    logger_registrations = logging.getLogger("registrations")

    logger_submissions.setLevel(logging.INFO)
    logger_logins.setLevel(logging.INFO)
    logger_registrations.setLevel(logging.INFO)

    log_dir = app.config["LOG_FOLDER"]
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logs = {
        "submissions": os.path.join(log_dir, "submissions.log"),
        "logins": os.path.join(log_dir, "logins.log"),
        "registrations": os.path.join(log_dir, "registrations.log"),
    }

    try:
        for log in logs.values():
            if not os.path.exists(log):
                open(log, "a").close()

        submission_log = logging.handlers.RotatingFileHandler(
            logs["submissions"], maxBytes=10000
        )
        login_log = logging.handlers.RotatingFileHandler(logs["logins"], maxBytes=10000)
        registration_log = logging.handlers.RotatingFileHandler(
            logs["registrations"], maxBytes=10000
        )

        logger_submissions.addHandler(submission_log)
        logger_logins.addHandler(login_log)
        logger_registrations.addHandler(registration_log)
    except IOError:
        pass

    stdout = logging.StreamHandler(stream=sys.stdout)

    logger_submissions.addHandler(stdout)
    logger_logins.addHandler(stdout)
    logger_registrations.addHandler(stdout)

    logger_submissions.propagate = 0
    logger_logins.propagate = 0
    logger_registrations.propagate = 0


def init_events(app):
    if app.config.get("CACHE_TYPE") == "redis":
        app.events_manager = RedisEventManager()
    elif app.config.get("CACHE_TYPE") == "filesystem":
        app.events_manager = EventManager()
    else:
        app.events_manager = EventManager()


def init_request_processors(app):
    @app.context_processor
    def inject_user():
        if session:
            return dict(session)
        return dict()

    @app.url_defaults
    def inject_theme(endpoint, values):
        if "theme" not in values and app.url_map.is_endpoint_expecting(
            endpoint, "theme"
        ):
            values["theme"] = ctf_theme()

    @app.before_request
    def needs_setup():
        if request.path == url_for("views.setup") or request.path.startswith("/themes"):
            return
        if not is_setup():
            return redirect(url_for("views.setup"))

    @app.before_request
    def tracker():
        if request.endpoint in ("views.themes", "views.custom_css"):
            return

        if authed():
            track = Tracking.query.filter_by(ip=get_ip(), user_id=session["id"]).first()
            if not track:
                visit = Tracking(ip=get_ip(), user_id=session["id"])
                db.session.add(visit)
            else:
                track.date = datetime.datetime.utcnow()

            try:
                db.session.commit()
            except (InvalidRequestError, IntegrityError):
                db.session.rollback()
                logout_user()

            if authed():
                user = get_current_user()
                team = get_current_team()

                if request.path.startswith("/themes") is False:
                    if user and user.banned:
                        return (
                            render_template(
                                "errors/403.html",
                                error="You have been banned from this CTF",
                            ),
                            403,
                        )

                    if team and team.banned:
                        return (
                            render_template(
                                "errors/403.html",
                                error="Your team has been banned from this CTF",
                            ),
                            403,
                        )

            db.session.close()

    @app.before_request
    def csrf():
        try:
            func = app.view_functions[request.endpoint]
        except KeyError:
            abort(404)
        if hasattr(func, "_bypass_csrf"):
            return
        if not session.get("nonce"):
            session["nonce"] = generate_nonce()
        if request.method not in ("GET", "HEAD", "OPTIONS", "TRACE"):
            if request.content_type == "application/json":
                if session["nonce"] != request.headers.get("CSRF-Token"):
                    abort(403)
            if request.content_type != "application/json":
                if session["nonce"] != request.form.get("nonce"):
                    abort(403)

    application_root = app.config.get("APPLICATION_ROOT")
    if application_root != "/":

        @app.before_request
        def force_subdirectory_redirect():
            if request.path.startswith(application_root) is False:
                return redirect(
                    application_root + request.script_root + request.full_path
                )

        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {application_root: app})
