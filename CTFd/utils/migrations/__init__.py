import os
import re
from pathlib import Path

from alembic.migration import MigrationContext
from flask import current_app as app
from flask_migrate import Migrate, stamp
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import create_database as create_database_util
from sqlalchemy_utils import database_exists as database_exists_util
from sqlalchemy_utils import drop_database as drop_database_util

migrations = Migrate()


def create_database():
    url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
    if url.drivername == "postgres":
        url.drivername = "postgresql"

    if url.drivername.startswith("mysql"):
        url.query["charset"] = "utf8mb4"

    # Creates database if the database database does not exist
    if not database_exists_util(url):
        if url.drivername.startswith("mysql"):
            create_database_util(url, encoding="utf8mb4")
        else:
            create_database_util(url)
    return url


def drop_database():
    url = make_url(app.config["SQLALCHEMY_DATABASE_URI"])
    if url.drivername == "postgres":
        url.drivername = "postgresql"
    drop_database_util(url)


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


def get_available_revisions():
    revisions = []
    directory = Path(os.path.dirname(app.root_path), "migrations", "versions")
    for f in directory.glob("*.py"):
        with f.open() as migration:
            revision = re.search(r'revision = "(.*?)"', migration.read()).group(1)
            revisions.append(revision)
    return revisions
