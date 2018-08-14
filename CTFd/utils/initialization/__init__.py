from flask import current_app as app, request, session, redirect, url_for, abort
from CTFd.models import db, Tracking

from CTFd.utils import markdown, get_config
from CTFd.utils.dates import unix_time_millis, unix_time

from CTFd.utils.config import can_register, can_send_mail, ctf_logo, ctf_name, ctf_theme, hide_scores
from CTFd.utils.config.pages import get_pages

from CTFd.utils.plugins import get_registered_stylesheets, get_registered_scripts, get_configurable_plugins

from CTFd.utils.user import authed, get_ip
from CTFd.utils.config import is_setup
from CTFd.utils.security.csrf import generate_nonce

from sqlalchemy.exc import InvalidRequestError, IntegrityError

import datetime


def init_template_filters(app):
    app.jinja_env.filters['markdown'] = markdown
    app.jinja_env.filters['unix_time'] = unix_time
    app.jinja_env.filters['unix_time_millis'] = unix_time_millis


def init_template_globals(app):
    app.jinja_env.globals.update(get_pages=get_pages)
    app.jinja_env.globals.update(can_register=can_register)
    app.jinja_env.globals.update(can_send_mail=can_send_mail)
    app.jinja_env.globals.update(ctf_name=ctf_name)
    app.jinja_env.globals.update(ctf_logo=ctf_logo)
    app.jinja_env.globals.update(ctf_theme=ctf_theme)
    app.jinja_env.globals.update(get_configurable_plugins=get_configurable_plugins)
    app.jinja_env.globals.update(get_registered_scripts=get_registered_scripts)
    app.jinja_env.globals.update(get_registered_stylesheets=get_registered_stylesheets)
    app.jinja_env.globals.update(get_config=get_config)
    app.jinja_env.globals.update(hide_scores=hide_scores)


def init_request_processors(app):
    @app.context_processor
    def inject_user():
        if session:
            return dict(session)
        return dict()

    @app.before_request
    def needs_setup():
        if request.path == '/setup' or request.path.startswith('/themes'):
            return
        if not is_setup():
            return redirect(url_for('views.setup'))

    @app.before_request
    def tracker():
        # TODO: This function shouldn't cause a DB hit.
        if authed():
            track = Tracking.query.filter_by(ip=get_ip(), user_id=session['id']).first()
            if not track:
                visit = Tracking(ip=get_ip(), user_id=session['id'])
                db.session.add(visit)
            else:
                track.date = datetime.datetime.utcnow()

            try:
                db.session.commit()
            except (InvalidRequestError, IntegrityError) as e:
                print(e.message)
                db.session.rollback()
                session.clear()

            db.session.close()

    @app.before_request
    def csrf():
        try:
            func = app.view_functions[request.endpoint]
        except KeyError:
            abort(404)
        if hasattr(func, '_bypass_csrf'):
            return
        if not session.get('nonce'):
            session['nonce'] = generate_nonce()
        if request.method == "POST":
            if session['nonce'] != request.form.get('nonce'):
                abort(403)

    @app.before_request
    def disable_jinja_cache():
        # TODO: Get rid of this function
        app.jinja_env.cache = {}
