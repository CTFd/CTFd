import os

from alembic.migration import MigrationContext
from flask import current_app as app
from flask_migrate import Migrate, stamp
from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import create_database as create_database_util
from sqlalchemy_utils import database_exists as database_exists_util

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
        if url.drivername.startswith("postgres"):
            print("Allowing don't create database due to permissions in Postgres")
            exists = True

    if not exists:
        if url.drivername.startswith("mysql"):
            create_database_util(url, encoding="utf8mb4")
        else:
            create_database_util(url)
    return url


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
