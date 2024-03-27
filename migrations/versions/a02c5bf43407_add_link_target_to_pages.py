"""Add link_target to Pages

Revision ID: a02c5bf43407
Revises: 9889b8c53673
Create Date: 2024-02-01 13:11:53.076825

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "a02c5bf43407"
down_revision = "9889b8c53673"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "pages", sa.Column("link_target", sa.String(length=80), nullable=True)
    )


def downgrade():
    op.drop_column("pages", "link_target")
