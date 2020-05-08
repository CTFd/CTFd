import inspect
import os

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from flask import current_app
from sqlalchemy import create_engine, pool

from CTFd.utils import get_config, set_config


def upgrade(plugin_name=None):
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

    engine = create_engine(database_url, poolclass=pool.NullPool)
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    op = Operations(context)

    # Find the list of migrations to run
    config = Config()
    config.set_main_option(
        "script_location",
        os.path.join(current_app.plugins_dir, plugin_name, "migrations"),
    )
    config.set_main_option(
        "version_locations",
        os.path.join(current_app.plugins_dir, plugin_name, "migrations"),
    )
    script = ScriptDirectory.from_config(config)

    # get current revision for plugin
    lower = get_config(plugin_name + "_alembic_version")
    upper = script.get_current_head()

    # Apply from lower to upper
    revs = list(script.iterate_revisions(lower=lower, upper=upper))
    revs.reverse()

    try:
        for r in revs:
            with context.begin_transaction():
                r.module.upgrade(op=op)
    finally:
        conn.close()

    # Set the new latest revision
    set_config(plugin_name + "_alembic_version", upper)
