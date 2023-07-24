"""Add func column to dynamic_challenges

Revision ID: eb68f277ab61
Revises: b37fb68807ea
Create Date: 2023-06-28 17:37:48.244827

"""
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "eb68f277ab61"
down_revision = "b37fb68807ea"
branch_labels = None
depends_on = None


def upgrade(op=None):
    op.add_column(
        "dynamic_challenge", sa.Column("function", sa.String(length=32), nullable=True)
    )
    conn = op.get_bind()
    url = str(conn.engine.url)
    if url.startswith("postgres"):
        conn.execute(
            "UPDATE dynamic_challenge SET function = 'logarithmic' WHERE function IS NULL"
        )
    else:
        conn.execute(
            "UPDATE dynamic_challenge SET `function` = 'logarithmic' WHERE `function` IS NULL"
        )


def downgrade(op=None):
    op.drop_column("dynamic_challenge", "function")
