import datetime
import json
import logging
import mistune
import os
import six

from collections import namedtuple
from flask import current_app as app, request, redirect, url_for, session, render_template, abort, jsonify
from flask_caching import Cache
from flask_migrate import Migrate, upgrade as migrate_upgrade, stamp as migrate_stamp

from sqlalchemy.exc import InvalidRequestError, IntegrityError

from CTFd.models import db, Challenges, WrongKeys, Pages, Config, Tracking, Teams, Files, ip2long, long2ip
from CTFd.utils.exports import CTFdSerializer
from CTFd.utils.user import get_ip

from datafreeze.format import SERIALIZERS

from CTFd.utils.dates import unix_time, unix_time_millis
from CTFd.utils.config.pages import get_pages
from CTFd.utils.config import (
    can_register,
    can_send_mail,
    ctf_name,
    ctf_logo,
    hide_scores,
    is_setup
)

if six.PY2:
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes

cache = Cache()
migrate = Migrate()
markdown = mistune.Markdown()
plugin_scripts = []
plugin_stylesheets = []


SERIALIZERS['ctfd'] = CTFdSerializer  # Load the custom serializer


def init_errors(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html', error=error.description), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html', error=error.description), 403

    @app.errorhandler(500)
    def general_error(error):
        return render_template('errors/500.html', error=error.description), 500

    @app.errorhandler(502)
    def gateway_error(error):
        return render_template('errors/502.html', error=error.description), 502


def init_utils(app):
    app.jinja_env.filters['markdown'] = markdown
    app.jinja_env.filters['unix_time'] = unix_time
    app.jinja_env.filters['unix_time_millis'] = unix_time_millis
    app.jinja_env.filters['long2ip'] = long2ip
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
        if authed():
            track = Tracking.query.filter_by(ip=get_ip(), team=session['id']).first()
            if not track:
                visit = Tracking(ip=get_ip(), team=session['id'])
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
            session['nonce'] = sha512(os.urandom(10))
        if request.method == "POST":
            if session['nonce'] != request.form.get('nonce'):
                abort(403)

    @app.before_request
    def disable_jinja_cache():
        app.jinja_env.cache = {}


def override_template(template, html):
    app.jinja_loader.overriden_templates[template] = html


def register_plugin_script(url):
    plugin_scripts.append(url)


def register_plugin_stylesheet(url):
    plugin_stylesheets.append(url)


def get_configurable_plugins():
    Plugin = namedtuple('Plugin', ['name', 'route'])

    plugins_path = os.path.join(app.root_path, 'plugins')
    plugin_directories = os.listdir(plugins_path)

    plugins = []

    for dir in plugin_directories:
        if os.path.isfile(os.path.join(plugins_path, dir, 'config.json')):
            path = os.path.join(plugins_path, dir, 'config.json')
            with open(path) as f:
                plugin_json_data = json.loads(f.read())
                p = Plugin(
                    name=plugin_json_data.get('name'),
                    route=plugin_json_data.get('route')
                )
                plugins.append(p)
        elif os.path.isfile(os.path.join(plugins_path, dir, 'config.html')):
            p = Plugin(
                name=dir,
                route='/admin/plugins/{}'.format(dir)
            )
            plugins.append(p)

    return plugins


def get_registered_scripts():
    return plugin_scripts


def get_registered_stylesheets():
    return plugin_stylesheets


@cache.memoize()
def get_app_config(key):
    value = app.config.get(key)
    return value


@cache.memoize()
def get_config(key):
    config = Config.query.filter_by(key=key).first()
    if config and config.value:
        value = config.value
        if value and value.isdigit():
            return int(value)
        elif value and isinstance(value, six.string_types):
            if value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False
            else:
                return value
    else:
        set_config(key, None)
        return None


def set_config(key, value):
    config = Config.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Config(key, value)
        db.session.add(config)
    db.session.commit()
    return config
