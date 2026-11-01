"""Set NULL challenge max_attempts to 0

Revision ID: b7d2e4f6a8c1
Revises: a3e1c5d7b9f2
Create Date: 2026-10-21 00:00:00.000000

"""

from alembic import op
from sqlalchemy.sql import column, table

from CTFd.models import db

# revision identifiers, used by Alembic.
revision = "b7d2e4f6a8c1"
down_revision = "a3e1c5d7b9f2"
branch_labels = None
depends_on = None

challenges_table = table(
    "challenges", column("id", db.Integer), column("max_attempts", db.Integer)
)


def upgrade():
    connection = op.get_bind()
    connection.execute(
        challenges_table.update()
        .where(challenges_table.c.max_attempts.is_(None))
        .values(max_attempts=0)
    )


def downgrade():
    pass
