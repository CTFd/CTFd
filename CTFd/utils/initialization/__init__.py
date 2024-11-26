import datetime
import logging
import os
import sys

from flask import abort, redirect, render_template, request, session, url_for
from sqlalchemy.exc import IntegrityError, InvalidRequestError
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from CTFd.cache import clear_user_recent_ips
from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.models import Tracking, db
from CTFd.utils import config, get_app_config, get_config, import_in_progress, markdown
from CTFd.utils.config import (
    can_send_mail,
    ctf_logo,
    ctf_name,
    ctf_theme,
    integrations,
    is_setup,
)
from CTFd.utils.config.pages import get_pages
from CTFd.utils.dates import isoformat, unix_time, unix_time_millis, unix_time_to_utc
from CTFd.utils.events import EventManager, RedisEventManager
from CTFd.utils.humanize.words import pluralize
from CTFd.utils.modes import generate_account_url, get_mode_as_word
from CTFd.utils.plugins import (
    get_configurable_plugins,
    get_menubar_plugins,
    get_registered_admin_scripts,
    get_registered_admin_stylesheets,
    get_registered_scripts,
    get_registered_stylesheets,
)
from CTFd.utils.security.auth import login_user, logout_user, lookup_user_token
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.user import (
    authed,
    get_current_team_attrs,
    get_current_user_attrs,
    get_current_user_recent_ips,
    get_ip,
    get_locale,
    is_admin,
)


def init_cli(app):
    from CTFd.cli import _cli

    app.register_blueprint(_cli, cli_group=None)


def init_template_filters(app):
    app.jinja_env.filters["markdown"] = markdown
    app.jinja_env.filters["unix_time"] = unix_time
    app.jinja_env.filters["unix_time_millis"] = unix_time_millis
    app.jinja_env.filters["unix_time_to_utc"] = unix_time_to_utc
    app.jinja_env.filters["isoformat"] = isoformat
    app.jinja_env.filters["pluralize"] = pluralize


def init_template_globals(app):
    from CTFd.constants import JINJA_ENUMS  # noqa: I001
    from CTFd.constants.assets import Assets
    from CTFd.constants.config import Configs
    from CTFd.constants.languages import Languages
    from CTFd.constants.plugins import Plugins
    from CTFd.constants.sessions import Session
    from CTFd.constants.static import Static
    from CTFd.constants.teams import Team
    from CTFd.constants.users import User
    from CTFd.forms import Forms
    from CTFd.utils.config.visibility import (
        accounts_visible,
        challenges_visible,
        registration_visible,
        scores_visible,
    )
    from CTFd.utils.countries import get_countries, lookup_country_code
    from CTFd.utils.countries.geoip import lookup_ip_address, lookup_ip_address_city

    app.jinja_env.globals.update(config=config)
    app.jinja_env.globals.update(get_pages=get_pages)
    app.jinja_env.globals.update(can_send_mail=can_send_mail)
    app.jinja_env.globals.update(get_ctf_name=ctf_name)
    app.jinja_env.globals.update(get_ctf_logo=ctf_logo)
    app.jinja_env.globals.update(get_ctf_theme=ctf_theme)
    app.jinja_env.globals.update(get_menubar_plugins=get_menubar_plugins)
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
    app.jinja_env.globals.update(lookup_ip_address=lookup_ip_address)
    app.jinja_env.globals.update(lookup_ip_address_city=lookup_ip_address_city)
    app.jinja_env.globals.update(accounts_visible=accounts_visible)
    app.jinja_env.globals.update(challenges_visible=challenges_visible)
    app.jinja_env.globals.update(registration_visible=registration_visible)
    app.jinja_env.globals.update(scores_visible=scores_visible)
    app.jinja_env.globals.update(get_mode_as_word=get_mode_as_word)
    app.jinja_env.globals.update(integrations=integrations)
    app.jinja_env.globals.update(authed=authed)
    app.jinja_env.globals.update(is_admin=is_admin)
    app.jinja_env.globals.update(get_current_user_attrs=get_current_user_attrs)
    app.jinja_env.globals.update(get_current_team_attrs=get_current_team_attrs)
    app.jinja_env.globals.update(get_ip=get_ip)
    app.jinja_env.globals.update(get_locale=get_locale)
    app.jinja_env.globals.update(Assets=Assets)
    app.jinja_env.globals.update(Configs=Configs)
    app.jinja_env.globals.update(Plugins=Plugins)
    app.jinja_env.globals.update(Session=Session)
    app.jinja_env.globals.update(Static=Static)
    app.jinja_env.globals.update(Forms=Forms)
    app.jinja_env.globals.update(User=User)
    app.jinja_env.globals.update(Team=Team)
    app.jinja_env.globals.update(Languages=Languages)

    # Add in JinjaEnums
    # The reason this exists is that on double import, JinjaEnums are not reinitialized
    # Thus, if you try to create two jinja envs (e.g. during testing), sometimes
    # an Enum will not be available to Jinja.
    # Instead we can just directly grab them from the persisted global dictionary.
    for k, v in JINJA_ENUMS.items():
        # .update() can't be used here because it would use the literal value k
        app.jinja_env.globals[k] = v


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
            logs["submissions"], maxBytes=10485760, backupCount=5
        )
        login_log = logging.handlers.RotatingFileHandler(
            logs["logins"], maxBytes=10485760, backupCount=5
        )
        registration_log = logging.handlers.RotatingFileHandler(
            logs["registrations"], maxBytes=10485760, backupCount=5
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
    app.events_manager.listen()


def init_request_processors(app):
    @app.url_defaults
    def inject_theme(endpoint, values):
        if "theme" not in values and app.url_map.is_endpoint_expecting(
            endpoint, "theme"
        ):
            values["theme"] = ctf_theme()

    @app.before_request
    def needs_setup():
        if import_in_progress():
            if request.endpoint == "admin.import_ctf":
                return
            else:
                return "Import currently in progress", 403
        if is_setup() is False:
            if request.endpoint in (
                "views.setup",
                "views.integrations",
                "views.themes",
                "views.files",
                "views.healthcheck",
                "views.robots",
            ):
                return
            else:
                return redirect(url_for("views.setup"))

    @app.before_request
    def tracker():
        if request.endpoint == "views.themes":
            return

        if import_in_progress():
            if request.endpoint == "admin.import_ctf":
                return
            else:
                return "Import currently in progress", 403

        if authed():
            user_ips = get_current_user_recent_ips()
            ip = get_ip()

            track = None
            if ip not in user_ips or request.method in (
                "POST",
                "PATCH",
                "DELETE",
            ):
                track = Tracking.query.filter_by(
                    ip=get_ip(), user_id=session["id"]
                ).first()

                if track:
                    track.date = datetime.datetime.utcnow()
                else:
                    track = Tracking(ip=get_ip(), user_id=session["id"])
                    db.session.add(track)

            if track:
                try:
                    db.session.commit()
                except (InvalidRequestError, IntegrityError):
                    db.session.rollback()
                    db.session.close()
                    logout_user()
                else:
                    clear_user_recent_ips(user_id=session["id"])

    @app.before_request
    def banned():
        if request.endpoint == "views.themes":
            return

        if authed():
            user = get_current_user_attrs()
            team = get_current_team_attrs()

            if user and user.banned:
                return (
                    render_template(
                        "errors/403.html", error="You have been banned from this CTF"
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

    @app.before_request
    def tokens():
        token = request.headers.get("Authorization")
        if token and (
            request.mimetype == "application/json"
            # Specially allow multipart/form-data for file uploads
            or (
                request.endpoint == "api.files_files_list"
                and request.method == "POST"
                and request.mimetype == "multipart/form-data"
            )
        ):
            try:
                token_type, token = token.split(" ", 1)
                user = lookup_user_token(token)
            except UserNotFoundException:
                abort(401)
            except UserTokenExpiredException:
                abort(401, description="Your access token has expired")
            except Exception:
                abort(401)
            else:
                login_user(user)

    @app.before_request
    def csrf():
        try:
            func = app.view_functions[request.endpoint]
        except KeyError:
            abort(404)
        if hasattr(func, "_bypass_csrf"):
            return
        if request.headers.get("Authorization"):
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

    @app.after_request
    def response_headers(response):
        response.headers["Cross-Origin-Opener-Policy"] = get_app_config(
            "CROSS_ORIGIN_OPENER_POLICY", default="same-origin-allow-popups"
        )
        return response

    application_root = app.config.get("APPLICATION_ROOT")
    if application_root != "/":

        @app.before_request
        def force_subdirectory_redirect():
            if request.path.startswith(application_root) is False:
                return redirect(
                    application_root + request.script_root + request.full_path
                )

        app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {application_root: app})
