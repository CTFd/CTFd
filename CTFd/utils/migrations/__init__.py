import os

from alembic.migration import MigrationContext
from flask import current_app as app
from flask_migrate import Migrate, stamp
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import create_database as create_database_util
from sqlalchemy_utils import database_exists as database_exists_util
from sqlalchemy_utils import drop_database as drop_database_util
from CTFd.utils.uploads import delete_file
from CTFd.cache import cache, clear_config, clear_standings, clear_pages
from CTFd.models import (
    Awards,
    Challenges,
    Configs,
    Notifications,
    Pages,
    Solves,
    Submissions,
    Teams,
    Tracking,
    Unlocks,
    Users,
    db,
)

migrations = Migrate()


def create_database():
    url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
    if url.drivername == "postgres":
        url.drivername = "postgresql"

    if url.drivername.startswith("mysql"):
        url.query["charset"] = "utf8mb4"

    # Creates database if the database does not exist
    try:
        # If the user don't have permission to access to "postres" databasen  this
        # will fail: https://github.com/kvesteri/sqlalchemy-utils/pull/372
        # in that case we asume that the database was previously created and we can't
        # drop or create the database
        exists = database_exists_util(url)
    except Exception:
        exists = True

    if not exists:
        if url.drivername.startswith("mysql"):
            create_database_util(url, encoding="utf8mb4")
        else:
            create_database_util(url)
    return url


def truncate_database():
    # delete all table data (but keep tables)
    _pages = Pages.query.all()
    for p in _pages:
        for f in p.files:
            delete_file(file_id=f.id)

    Pages.query.delete()

    Notifications.query.delete()

    _challenges = Challenges.query.all()
    for c in _challenges:
        for f in c.files:
            delete_file(file_id=f.id)
    Challenges.query.delete()

    Users.query.delete()
    Teams.query.delete()

    Solves.query.delete()
    Submissions.query.delete()
    Awards.query.delete()
    Unlocks.query.delete()
    Tracking.query.delete()

    Configs.query.delete()
    clear_config()
    clear_pages()
    clear_standings()
    cache.clear()

    db.session.commit()


def drop_database():
    try:
        url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
        if url.drivername == "postgres":
            url.drivername = "postgresql"
        drop_database_util(url)
        return True
    except Exception:
        # Drop database failed
        return False


def get_current_revision():
    engine = create_engine(app.config.get("SQLALCHEMY_DATABASE_URI"))
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    current_rev = context.get_current_revision()
    return current_rev


def stamp_latest_revision():
    # Get proper migrations directory regardless of cwd
    directory = os.path.join(os.path.dirname(app.root_path), "migrations")
    stamp(directory=directory)
