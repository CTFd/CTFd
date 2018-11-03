from flask import current_app as app
from flask_migrate import Migrate, migrate, upgrade, stamp, current
from alembic.migration import MigrationContext
from sqlalchemy import create_engine
from six import StringIO

migrations = Migrate()


def get_current_revision():
    engine = create_engine(app.config.get('SQLALCHEMY_DATABASE_URI'))
    conn = engine.connect()
    context = MigrationContext.configure(conn)
    current_rev = context.get_current_revision()
    return current_rev
