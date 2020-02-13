"""add theme code injections to configs

Revision ID: a03403986a32
Revises: 080d29b15cd3
Create Date: 2020-02-13 01:10:16.430424

"""
from CTFd.utils import get_config, set_config


# revision identifiers, used by Alembic.
revision = "a03403986a32"
down_revision = "080d29b15cd3"
branch_labels = None
depends_on = None


def upgrade():
    css = get_config("css")
    if css:
        new_css = "<style>\n" + css + "\n</style>"
        set_config("theme_header", new_css)


def downgrade():
    pass
