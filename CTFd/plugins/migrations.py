import inspect  # noqa: I001
import os

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from flask import current_app
from sqlalchemy import create_engine
from sqlalchemy import inspect as SQLAInspect
from sqlalchemy import pool

from CTFd.utils import _get_config, set_config


def get_all_tables(op):
    """
    Function to list all the tables in the database from a migration
    """
    inspector = SQLAInspect(op.get_bind())
    tables = inspector.get_table_names()
    return tables


def get_columns_for_table(op, table_name, names_only=False):
    """
    Function to list the columns in a table from a migration
    """
    inspector = SQLAInspect(op.get_bind())
    columns = inspector.get_columns(table_name)
    if names_only is True:
        columns = [c["name"] for c in columns]
    return columns


def current(plugin_name=None):
    if plugin_name is None:
        # Get the directory name of the plugin if unspecified
        # Doing it this way doesn't waste the rest of the inspect.stack call
        frame = inspect.currentframe()
        caller_info = inspect.getframeinfo(frame.f_back)
        caller_path = caller_info[0]
        plugin_name = os.path.basename(os.path.dirname(caller_path))

    # Specifically bypass the cached config so that we always get the database value
    version = _get_config.__wrapped__(plugin_name + "_alembic_version")
    if version == KeyError:
        version = None
    return version


def upgrade(plugin_name=None, revision=None, lower="current"):
    database_url = current_app.config.get("SQLALCHEMY_DATABASE_URI")
    if database_url.startswith("sqlite"):
        current_app.db.create_all()
        return

    if plugin_name is None:
        # Get the directory name of the plugin if unspecified
        # Doing it this way doesn't waste the rest of the inspect.stack call
        frame = inspect.currentframe()
        caller_info = inspect.getframeinfo(frame.f_back)
        caller_path = caller_info[0]
        plugin_name = os.path.basename(os.path.dirname(caller_path))

    # Check if the plugin has migraitons
    migrations_path = os.path.join(current_app.plugins_dir, plugin_name, "migrations")
    if os.path.isdir(migrations_path) is False:
        return

    engine = create_engine(database_url, poolclass=pool.NullPool)
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    op = Operations(context)

    # Find the list of migrations to run
    config = Config()
    config.set_main_option("script_location", migrations_path)
    config.set_main_option("version_locations", migrations_path)
    script = ScriptDirectory.from_config(config)

    # Choose base revision for plugin upgrade
    # "current" points to the current plugin version stored in config
    # None represents the absolute base layer (e.g. first installation)
    if lower == "current":
        lower = current(plugin_name)

    # Do we upgrade to head or to a specific revision
    if revision is None:
        upper = script.get_current_head()
    else:
        upper = revision

    # Apply from lower to upper
    revs = list(script.iterate_revisions(lower=lower, upper=upper))
    revs.reverse()

    try:
        for r in revs:
            with context.begin_transaction():
                r.module.upgrade(op=op)
            # Set revision that succeeded so we don't need
            # to start from the beginning on failure
            set_config(plugin_name + "_alembic_version", r.revision)
    finally:
        conn.close()

    # Set the new latest revision
    set_config(plugin_name + "_alembic_version", upper)
