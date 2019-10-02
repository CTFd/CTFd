import sys
import os

from distutils.version import StrictVersion
from flask import Flask, Request
from flask_migrate import upgrade
from werkzeug.utils import cached_property
from werkzeug.middleware.proxy_fix import ProxyFix
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from six.moves import input

from CTFd import utils
from CTFd.utils.migrations import migrations, create_database, stamp_latest_revision
from CTFd.utils.sessions import CachingSessionInterface
from CTFd.utils.updates import update_check
from CTFd.utils.initialization import (
    init_request_processors,
    init_template_filters,
    init_template_globals,
    init_logs,
    init_events,
)
from CTFd.plugins import init_plugins

# Hack to support Unicode in Python 2 properly
if sys.version_info[0] < 3:
    reload(sys)  # noqa: F821
    sys.setdefaultencoding("utf-8")

__version__ = "2.1.5"


class CTFdRequest(Request):
    @cached_property
    def path(self):
        """
        Hijack the original Flask request path because it does not account for subdirectory deployments in an intuitive
        manner. We append script_root so that the path always points to the full path as seen in the browser.
        e.g. /subdirectory/path/route vs /path/route

        :return: string
        """
        return self.script_root + super(CTFdRequest, self).path


class CTFdFlask(Flask):
    def __init__(self, *args, **kwargs):
        """Overriden Jinja constructor setting a custom jinja_environment"""
        self.jinja_environment = SandboxedBaseEnvironment
        self.session_interface = CachingSessionInterface(key_prefix="session")
        self.request_class = CTFdRequest
        Flask.__init__(self, *args, **kwargs)

    def create_jinja_environment(self):
        """Overridden jinja environment constructor"""
        return super(CTFdFlask, self).create_jinja_environment()


class SandboxedBaseEnvironment(SandboxedEnvironment):
    """SandboxEnvironment that mimics the Flask BaseEnvironment"""

    def __init__(self, app, **options):
        if "loader" not in options:
            options["loader"] = app.create_global_jinja_loader()
        # Disable cache entirely so that themes can be switched (#662)
        # If the cache is enabled, switching themes will cause odd rendering errors
        SandboxedEnvironment.__init__(self, cache_size=0, **options)
        self.app = app


class ThemeLoader(FileSystemLoader):
    """Custom FileSystemLoader that switches themes based on the configuration value"""

    def __init__(self, searchpath, encoding="utf-8", followlinks=False):
        super(ThemeLoader, self).__init__(searchpath, encoding, followlinks)
        self.overriden_templates = {}

    def get_source(self, environment, template):
        # Check if the template has been overriden
        if template in self.overriden_templates:
            return self.overriden_templates[template], template, True

        # Check if the template requested is for the admin panel
        if template.startswith("admin/"):
            template = template[6:]  # Strip out admin/
            template = "/".join(["admin", "templates", template])
            return super(ThemeLoader, self).get_source(environment, template)

        # Load regular theme data
        theme = utils.get_config("ctf_theme")
        template = "/".join([theme, "templates", template])
        return super(ThemeLoader, self).get_source(environment, template)


def confirm_upgrade():
    if sys.stdin.isatty():
        print("/*\\ CTFd has updated and must update the database! /*\\")
        print("/*\\ Please backup your database before proceeding! /*\\")
        print("/*\\ CTFd maintainers are not responsible for any data loss! /*\\")
        if input("Run database migrations (Y/N)").lower().strip() == "y":
            return True
        else:
            print("/*\\ Ignored database migrations... /*\\")
            return False
    else:
        return True


def run_upgrade():
    upgrade()
    utils.set_config("ctf_version", __version__)


def create_app(config="CTFd.config.Config"):
    app = CTFdFlask(__name__)
    with app.app_context():
        app.config.from_object(config)

        theme_loader = ThemeLoader(
            os.path.join(app.root_path, "themes"), followlinks=True
        )
        app.jinja_loader = theme_loader

        from CTFd.models import (  # noqa: F401
            db,
            Teams,
            Solves,
            Challenges,
            Fails,
            Flags,
            Tags,
            Files,
            Tracking,
        )

        url = create_database()

        # This allows any changes to the SQLALCHEMY_DATABASE_URI to get pushed back in
        # This is mostly so we can force MySQL's charset
        app.config["SQLALCHEMY_DATABASE_URI"] = str(url)

        # Register database
        db.init_app(app)

        # Register Flask-Migrate
        migrations.init_app(app, db)

        # Alembic sqlite support is lacking so we should just create_all anyway
        if url.drivername.startswith("sqlite"):
            db.create_all()
            stamp_latest_revision()
        else:
            # This creates tables instead of db.create_all()
            # Allows migrations to happen properly
            upgrade()

        from CTFd.models import ma

        ma.init_app(app)

        app.db = db
        app.VERSION = __version__

        from CTFd.cache import cache

        cache.init_app(app)
        app.cache = cache

        reverse_proxy = app.config.get("REVERSE_PROXY")
        if reverse_proxy:
            if "," in reverse_proxy:
                proxyfix_args = [int(i) for i in reverse_proxy.split(",")]
                app.wsgi_app = ProxyFix(app.wsgi_app, None, *proxyfix_args)
            else:
                app.wsgi_app = ProxyFix(
                    app.wsgi_app,
                    num_proxies=None,
                    x_for=1,
                    x_proto=1,
                    x_host=1,
                    x_port=1,
                    x_prefix=1,
                )

        version = utils.get_config("ctf_version")

        # Upgrading from an older version of CTFd
        if version and (StrictVersion(version) < StrictVersion(__version__)):
            if confirm_upgrade():
                run_upgrade()
            else:
                exit()

        if not version:
            utils.set_config("ctf_version", __version__)

        if not utils.get_config("ctf_theme"):
            utils.set_config("ctf_theme", "core")

        update_check(force=True)

        init_request_processors(app)
        init_template_filters(app)
        init_template_globals(app)

        # Importing here allows tests to use sensible names (e.g. api instead of api_bp)
        from CTFd.views import views
        from CTFd.teams import teams
        from CTFd.users import users
        from CTFd.challenges import challenges
        from CTFd.scoreboard import scoreboard
        from CTFd.auth import auth
        from CTFd.admin import admin
        from CTFd.api import api
        from CTFd.events import events
        from CTFd.errors import page_not_found, forbidden, general_error, gateway_error

        app.register_blueprint(views)
        app.register_blueprint(teams)
        app.register_blueprint(users)
        app.register_blueprint(challenges)
        app.register_blueprint(scoreboard)
        app.register_blueprint(auth)
        app.register_blueprint(api)
        app.register_blueprint(events)

        app.register_blueprint(admin)

        app.register_error_handler(404, page_not_found)
        app.register_error_handler(403, forbidden)
        app.register_error_handler(500, general_error)
        app.register_error_handler(502, gateway_error)

        init_logs(app)
        init_events(app)
        init_plugins(app)

        return app
