import os

from distutils.version import StrictVersion
from flask import Flask
from jinja2 import FileSystemLoader
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import database_exists, create_database

from utils import get_config, set_config, cache, migrate, migrate_upgrade

__version__ = '1.0.0'

class ThemeLoader(FileSystemLoader):
    def get_source(self, environment, template):
        if template.startswith('admin/'):
            return super(ThemeLoader, self).get_source(environment, template)
        theme = get_config('ctf_theme')
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

        db.init_app(app)

        try:
            if not (url.drivername.startswith('sqlite') or database_exists(url)):
                create_database(url)
            db.create_all()
        except OperationalError:
            db.create_all()
        except ProgrammingError:  ## Database already exists
            pass
        else:
            db.create_all()

        app.db = db

        migrate.init_app(app, db)

        cache.init_app(app)
        app.cache = cache

        version = get_config('ctf_version')

        if not version: ## Upgrading from an unversioned CTFd
            set_config('ctf_version', __version__)

        if version and (StrictVersion(version) < StrictVersion(__version__)): ## Upgrading from an older version of CTFd
            migrate_upgrade()
            set_config('ctf_version', __version__)
            
        if not get_config('ctf_theme'):
            set_config('ctf_theme', 'original')

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

        from CTFd.plugins import init_plugins

        init_plugins(app)

        return app
