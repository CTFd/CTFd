"""add theme code injections to configs

Revision ID: a03403986a32
Revises: 080d29b15cd3
Create Date: 2020-02-13 01:10:16.430424

"""
from CTFd.models import db, Configs


# revision identifiers, used by Alembic.
revision = "a03403986a32"
down_revision = "080d29b15cd3"
branch_labels = None
depends_on = None


def upgrade():
    css = Configs.query.filter_by(key="css").first()
    if css and css.value:
        new_css = "<style>\n" + css.value + "\n</style>"
        config = Configs.query.filter_by(key="theme_header").first()
        if config:
            config.value = new_css
        else:
            config = Configs(key="theme_header", value=new_css)
            db.session.add(config)
        db.session.commit()


def downgrade():
    pass
