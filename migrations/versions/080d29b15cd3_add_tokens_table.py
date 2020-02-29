"""Add Tokens table to store user access tokens

Revision ID: 080d29b15cd3
Revises: b295b033364d
Create Date: 2019-11-03 18:21:04.827015

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "080d29b15cd3"
down_revision = "b295b033364d"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created", sa.DateTime(), nullable=True),
        sa.Column("expiration", sa.DateTime(), nullable=True),
        sa.Column("value", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("value"),
    )


def downgrade():
    op.drop_table("tokens")
