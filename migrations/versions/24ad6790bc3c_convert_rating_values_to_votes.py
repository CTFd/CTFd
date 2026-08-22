"""Convert rating values to votes

Revision ID: 24ad6790bc3c
Revises: 55623b100da8
Create Date: 2025-09-03 05:19:54.151054

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "24ad6790bc3c"
down_revision = "55623b100da8"
branch_labels = None
depends_on = None


def upgrade():
    # Convert 5-star ratings to upvote/downvote system
    # Values 1-2 become -1 (downvote)
    # Values 3-5 become 1 (upvote)

    connection = op.get_bind()

    # Update ratings with values 1 or 2 to -1 (downvote)
    connection.execute(sa.text("UPDATE ratings SET value = -1 WHERE value IN (1, 2)"))

    # Update ratings with values 3, 4, or 5 to 1 (upvote)
    connection.execute(sa.text("UPDATE ratings SET value = 1 WHERE value IN (3, 4, 5)"))


def downgrade():
    # This downgrade is not reversible since we lose the original 5-star granularity
    # We can only convert back to a simplified 5-star system
    # -1 (downvote) becomes 1 (1 star)
    # 1 (upvote) becomes 5 (5 stars)

    connection = op.get_bind()

    # Convert downvotes (-1) to 1-star ratings
    connection.execute(sa.text("UPDATE ratings SET value = 1 WHERE value = -1"))

    # Convert upvotes (1) to 5-star ratings
    connection.execute(sa.text("UPDATE ratings SET value = 5 WHERE value = 1"))
