"""Add description column to tokens table

Revision ID: 9e6f6578ca84
Revises: 0def790057c1
Create Date: 2023-06-21 23:22:34.179636

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9e6f6578ca84"
down_revision = "0def790057c1"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tokens", sa.Column("description", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("tokens", "description")
