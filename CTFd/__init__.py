import os

from distutils.version import StrictVersion
from flask import Flask
from jinja2 import FileSystemLoader
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy_utils import database_exists, create_database
from six.moves import input

from CTFd.utils import cache, migrate, migrate_upgrade, migrate_stamp
from CTFd import utils

__version__ = '1.0.2'

class ThemeLoader(FileSystemLoader):
    def get_source(self, environment, template):
        if template.startswith('admin/'):
            return super(ThemeLoader, self).get_source(environment, template)
        theme = utils.get_config('ctf_theme')
        template = "/".join([theme, template])
        return super(ThemeLoader, self).get_source(environment, template)


def create_app(config='CTFd.config.Config'):
    app = Flask(__name__)
    with app.app_context():
        app.config.from_object(config)
        app.jinja_loader = ThemeLoader(os.path.join(app.root_path, app.template_folder), followlinks=True)

        from CTFd.models import db, Teams, Solves, Challenges, WrongKeys, Keys, Tags, Files, Tracking

        url = make_url(app.config['SQLALCHEMY_DATABASE_URI'])
        if url.drivername == 'postgres':
            url.drivername = 'postgresql'

        ## Creates database if the database database does not exist
        if not database_exists(url):
            create_database(url)

        ## Register database
        db.init_app(app)

        ## Register Flask-Migrate
        migrate.init_app(app, db)

        ## This creates tables instead of db.create_all()
        ## Allows migrations to happen properly
        migrate_upgrade()

        ## Alembic sqlite support is lacking so we should just create_all anyway
        if url.drivername.startswith('sqlite'):
            db.create_all()

        app.db = db

        cache.init_app(app)
        app.cache = cache

        version = utils.get_config('ctf_version')

        if not version: ## Upgrading from an unversioned CTFd
            utils.set_config('ctf_version', __version__)

        if version and (StrictVersion(version) < StrictVersion(__version__)): ## Upgrading from an older version of CTFd
            print("/*\\ CTFd has updated and must update the database! /*\\")
            print("/*\\ Please backup your database before proceeding! /*\\")
            print("/*\\ CTFd maintainers are not responsible for any data loss! /*\\")
            if input('Run database migrations (Y/N)').lower().strip() == 'y':
                migrate_stamp()
                migrate_upgrade()
                utils.set_config('ctf_version', __version__)
            else:
                print('/*\\ Ignored database migrations... /*\\')
                exit()

        if not utils.get_config('ctf_theme'):
            utils.set_config('ctf_theme', 'original')

        from CTFd.views import views
        from CTFd.challenges import challenges
        from CTFd.scoreboard import scoreboard
        from CTFd.auth import auth
        from CTFd.admin import admin, admin_statistics, admin_challenges, admin_pages, admin_scoreboard, admin_containers, admin_keys, admin_teams
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
        app.register_blueprint(admin_containers)
        app.register_blueprint(admin_pages)

        from CTFd.plugins import init_plugins

        init_plugins(app)

        return app
