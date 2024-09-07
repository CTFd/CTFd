"""Add attribution to Challenges

Revision ID: 4fe3eeed9a9d
Revises: a02c5bf43407
Create Date: 2024-09-07 01:02:28.997761

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4fe3eeed9a9d"
down_revision = "a02c5bf43407"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("challenges", sa.Column("attribution", sa.Text(), nullable=True))


def downgrade():
    op.drop_column("challenges", "attribution")
