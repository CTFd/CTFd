"""add users mfa table

Revision ID: c42ecf16f8b2
Revises: 48d8250d19bd
Create Date: 2026-02-16 00:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c42ecf16f8b2"
down_revision = "48d8250d19bd"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users_mfa",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("totp_secret", sa.Text(), nullable=False),
        sa.Column("backup_codes", sa.Text(), nullable=False),
        sa.Column("last_used", sa.DateTime(), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=False),
        sa.Column("updated", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )


def downgrade():
    op.drop_table("users_mfa")
