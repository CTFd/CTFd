"""Add scheduled_at column to Challenges

Revision ID: 8275865e5992
Revises: e69a79ebffd3
Create Date: 2026-07-16 05:06:15.905263

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8275865e5992"
down_revision = "e69a79ebffd3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("challenges", sa.Column("scheduled_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("challenges", "scheduled_at")
