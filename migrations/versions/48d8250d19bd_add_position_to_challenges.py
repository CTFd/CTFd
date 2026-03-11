"""Add position to challenges

Revision ID: 48d8250d19bd
Revises: 67ebab6de598
Create Date: 2026-01-15 09:57:05.472760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "48d8250d19bd"
down_revision = "67ebab6de598"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "challenges",
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade():
    op.drop_column("challenges", "position")
