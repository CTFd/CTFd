"""Add language column to Users table

Revision ID: 0def790057c1
Revises: 46a278193a94
Create Date: 2023-04-19 00:56:54.592584

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0def790057c1"
down_revision = "46a278193a94"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("language", sa.String(length=32), nullable=True))


def downgrade():
    op.drop_column("users", "language")
