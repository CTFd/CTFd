"""Add Brackets table

Revision ID: 9889b8c53673
Revises: 5c4996aeb2cb
Create Date: 2024-01-25 03:17:52.734753

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "9889b8c53673"
down_revision = "5c4996aeb2cb"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "brackets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("type", sa.String(length=80), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("teams", sa.Column("bracket_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "teams", "brackets", ["bracket_id"], ["id"], ondelete="SET NULL"
    )
    op.drop_column("teams", "bracket")
    op.add_column("users", sa.Column("bracket_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        None, "users", "brackets", ["bracket_id"], ["id"], ondelete="SET NULL"
    )
    op.drop_column("users", "bracket")


def downgrade():
    op.add_column(
        "users", sa.Column("bracket", mysql.VARCHAR(length=32), nullable=True)
    )
    op.drop_constraint(None, "users", type_="foreignkey")
    op.drop_column("users", "bracket_id")
    op.add_column(
        "teams", sa.Column("bracket", mysql.VARCHAR(length=32), nullable=True)
    )
    op.drop_constraint(None, "teams", type_="foreignkey")
    op.drop_column("teams", "bracket_id")
    op.drop_table("brackets")
