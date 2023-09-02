"""Add solution column to Challenges

Revision ID: f69787339de7
Revises: 9e6f6578ca84
Create Date: 2023-08-30 14:55:23.569321

"""
from alembic import op  # noqa: I001
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f69787339de7"
down_revision = "9e6f6578ca84"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("challenges", sa.Column("solution", sa.Text(), nullable=True))
    op.add_column("challenges", sa.Column("solution_state", sa.String(length=80), nullable=False)),

def downgrade():
    op.drop_column("challenges", "solution_state")
    op.drop_column("challenges", "solution")
