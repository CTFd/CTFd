"""Add scheduled_at column to Challenges

Revision ID: 6315852a7255
Revises: fb9b5ff9b15e
Create Date: 2026-05-27 14:31:55.231535

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6315852a7255"
down_revision = "fb9b5ff9b15e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("challenges", sa.Column("scheduled_at", sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column("challenges", "scheduled_at")
