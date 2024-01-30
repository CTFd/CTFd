"""Add sha1sum field to Files

Revision ID: 5c4996aeb2cb
Revises: 9e6f6578ca84
Create Date: 2024-01-07 13:09:08.843903

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5c4996aeb2cb"
down_revision = "9e6f6578ca84"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("files", sa.Column("sha1sum", sa.String(length=40), nullable=True))


def downgrade():
    op.drop_column("files", "sha1sum")
