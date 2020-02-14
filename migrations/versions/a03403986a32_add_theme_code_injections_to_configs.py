"""add theme code injections to configs

Revision ID: a03403986a32
Revises: 080d29b15cd3
Create Date: 2020-02-13 01:10:16.430424

"""
from alembic import op
from sqlalchemy.sql import column, table

from CTFd.models import db


# revision identifiers, used by Alembic.
revision = "a03403986a32"
down_revision = "080d29b15cd3"
branch_labels = None
depends_on = None

configs_table = table(
    "config", column("id", db.Integer), column("key", db.Text), column("value", db.Text)
)


def upgrade():
    connection = op.get_bind()
    css = connection.execute(
        configs_table.select().where(configs_table.c.key == "css").limit(1)
    ).fetchone()

    if css and css.value:
        new_css = "<style>\n" + css.value + "\n</style>"
        config = connection.execute(
            configs_table.select().where(configs_table.c.key == "theme_header").limit(1)
        ).fetchone()
        if config:
            # Do not overwrite existing theme_header value
            pass
        else:
            connection.execute(
                configs_table.insert().values(key="theme_header", value=new_css)
            )


def downgrade():
    pass
