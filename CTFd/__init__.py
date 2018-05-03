import sys
import os

from distutils.version import StrictVersion
from flask import Flask
from jinja2 import FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import database_exists, create_database
from six.moves import input

from CTFd.utils import cache, migrate, migrate_upgrade, migrate_stamp, update_check
from CTFd import utils

# Hack to support Unicode in Python 2 properly
if sys.version_info[0] < 3:
    reload(sys)
    sys.setdefaultencoding("utf-8")

__version__ = '1.2.0'


class CTFdFlask(Flask):
    def __init__(self, *args, **kwargs):
        """Overriden Jinja constructor setting a custom jinja_environment"""
        self.jinja_environment = SandboxedBaseEnvironment
        Flask.__init__(self, *args, **kwargs)

    def create_jinja_environment(self):
        """Overridden jinja environment constructor"""
        return super(CTFdFlask, self).create_jinja_environment()


class SandboxedBaseEnvironment(SandboxedEnvironment):
    """SandboxEnvironment that mimics the Flask BaseEnvironment"""
    def __init__(self, app, **options):
        if 'loader' not in options:
            options['loader'] = app.create_global_jinja_loader()
        SandboxedEnvironment.__init__(self, **options)
        self.app = app


class ThemeLoader(FileSystemLoader):
    """Custom FileSystemLoader that switches themes based on the configuration value"""
    def __init__(self, searchpath, encoding='utf-8', followlinks=False):
        super(ThemeLoader, self).__init__(searchpath, encoding, followlinks)
        self.overriden_templates = {}

    def get_source(self, environment, template):
        # Check if the template has been overriden
        if template in self.overriden_templates:
            return self.overriden_templates[template], template, True

        # Check if the template requested is for the admin panel
        if template.startswith('admin/'):
            template = template[6:]  # Strip out admin/
            template = "/".join(['admin', 'templates', template])
            return super(ThemeLoader, self).get_source(environment, template)

        # Load regular theme data
        theme = utils.get_config('ctf_theme')
        template = "/".join([theme, 'templates', template])
        return super(ThemeLoader, self).get_source(environment, template)


def confirm_upgrade():
    if sys.stdin.isatty():
        print("/*\\ CTFd has updated and must update the database! /*\\")
        print("/*\\ Please backup your database before proceeding! /*\\")
        print("/*\\ CTFd maintainers are not responsible for any data loss! /*\\")
        if input('Run database migrations (Y/N)').lower().strip() == 'y':
            return True
        else:
            print('/*\\ Ignored database migrations... /*\\')
            return False
    else:
        return True


def run_upgrade():
    migrate_upgrade()
    utils.set_config('ctf_version', __version__)


def create_app(config='CTFd.config.Config'):
    app = CTFdFlask(__name__)
    with app.app_context():
        app.config.from_object(config)

        theme_loader = ThemeLoader(os.path.join(app.root_path, 'themes'), followlinks=True)
        app.jinja_loader = theme_loader

        from CTFd.models import db, Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking

        url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
        if url.drivername == 'postgres':
            url.drivername = 'postgresql'

        if url.drivername.startswith('mysql'):
            url.query['charset'] = 'utf8mb4'

        # Creates database if the database database does not exist
        if not database_exists(url):
            if url.drivername.startswith('mysql'):
                create_database(url, encoding='utf8mb4')
            else:
                create_database(url)

        # This allows any changes to the SQLALCHEMY_DATABASE_URI to get pushed back in
        # This is mostly so we can force MySQL's charset
        app.config['SQLALCHEMY_DATABASE_URI'] = str(url)

        # Register database
        db.init_app(app)

        # Register Flask-Migrate
        migrate.init_app(app, db)

        # Alembic sqlite support is lacking so we should just create_all anyway
        if url.drivername.startswith('sqlite'):
            db.create_all()
        else:
            if len(db.engine.table_names()) == 0:
                # This creates tables instead of db.create_all()
                # Allows migrations to happen properly
                migrate_upgrade()
            elif 'alembic_version' not in db.engine.table_names():
                # There is no alembic_version because CTFd is from before it had migrations
                # Stamp it to the base migration
                if confirm_upgrade():
                    migrate_stamp(revision='cb3cfcc47e2f')
                    run_upgrade()
                else:
                    exit()

        app.db = db
        app.VERSION = __version__

        cache.init_app(app)
        app.cache = cache

        update_check(force=True)

        version = utils.get_config('ctf_version')

        # Upgrading from an older version of CTFd
        if version and (StrictVersion(version) < StrictVersion(__version__)):
            if confirm_upgrade():
                run_upgrade()
            else:
                exit()

        if not version:
            utils.set_config('ctf_version', __version__)

        if not utils.get_config('ctf_theme'):
            utils.set_config('ctf_theme', 'core')

        from CTFd.views import views
        from CTFd.challenges import challenges
        from CTFd.scoreboard import scoreboard
        from CTFd.auth import auth
        from CTFd.admin import admin, admin_statistics, admin_challenges, admin_pages, admin_scoreboard, admin_keys, admin_teams
        from CTFd.utils import init_utils, init_errors, init_logs

        init_utils(app)
        init_errors(app)
        init_logs(app)

        app.register_blueprint(views)
        app.register_blueprint(challenges)
        app.register_blueprint(scoreboard)
        app.register_blueprint(auth)

        app.register_blueprint(admin)
        app.register_blueprint(admin_statistics)
        app.register_blueprint(admin_challenges)
        app.register_blueprint(admin_teams)
        app.register_blueprint(admin_scoreboard)
        app.register_blueprint(admin_keys)
        app.register_blueprint(admin_pages)

        from CTFd.plugins import init_plugins

        init_plugins(app)

        return app
