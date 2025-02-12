"""add title to hint

Revision ID: a49ad66aa0f1
Revises: 4fe3eeed9a9d
Create Date: 2025-02-10 14:45:00.933880

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "a49ad66aa0f1"
down_revision = "4fe3eeed9a9d"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("hints", sa.Column("title", sa.String(length=80), nullable=True))


def downgrade():
    op.drop_column("hints", "title")
