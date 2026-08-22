"""Add dynamic prefix to dynamic_challenge table

Revision ID: 93284ed9c099
Revises: eb68f277ab61
Create Date: 2025-10-10 02:07:16.055798

"""
import sqlalchemy as sa

from CTFd.plugins.migrations import get_columns_for_table

# revision identifiers, used by Alembic.
revision = "93284ed9c099"
down_revision = "eb68f277ab61"
branch_labels = None
depends_on = None


def upgrade(op=None):
    columns = get_columns_for_table(
        op=op, table_name="dynamic_challenge", names_only=True
    )
    # Add new columns with dynamic_ prefix
    if "dynamic_initial" not in columns:
        op.add_column(
            "dynamic_challenge",
            sa.Column("dynamic_initial", sa.Integer(), nullable=True),
        )
    if "dynamic_minimum" not in columns:
        op.add_column(
            "dynamic_challenge",
            sa.Column("dynamic_minimum", sa.Integer(), nullable=True),
        )
    if "dynamic_decay" not in columns:
        op.add_column(
            "dynamic_challenge", sa.Column("dynamic_decay", sa.Integer(), nullable=True)
        )
    if "dynamic_function" not in columns:
        op.add_column(
            "dynamic_challenge",
            sa.Column("dynamic_function", sa.String(length=32), nullable=True),
        )

    # Copy data from old columns to new columns
    connection = op.get_bind()
    url = str(connection.engine.url)
    if url.startswith("postgres"):
        connection.execute(
            sa.text(
                """
                UPDATE dynamic_challenge
                SET dynamic_initial = initial,
                    dynamic_minimum = minimum,
                    dynamic_decay = decay,
                    dynamic_function = function
            """
            )
        )
    else:
        connection.execute(
            sa.text(
                """
                UPDATE dynamic_challenge
                SET dynamic_initial = initial,
                    dynamic_minimum = minimum,
                    dynamic_decay = decay,
                    dynamic_function = `function`
            """
            )
        )

    # Drop old columns
    if "minimum" in columns:
        op.drop_column("dynamic_challenge", "minimum")
    if "initial" in columns:
        op.drop_column("dynamic_challenge", "initial")
    if "function" in columns:
        op.drop_column("dynamic_challenge", "function")
    if "decay" in columns:
        op.drop_column("dynamic_challenge", "decay")


def downgrade(op=None):
    columns = get_columns_for_table(
        op=op, table_name="dynamic_challenge", names_only=True
    )
    # Add old columns back
    if "decay" not in columns:
        op.add_column(
            "dynamic_challenge", sa.Column("decay", sa.Integer(), nullable=True)
        )
    if "function" not in columns:
        op.add_column(
            "dynamic_challenge",
            sa.Column("function", sa.String(length=32), nullable=True),
        )
    if "initial" not in columns:
        op.add_column(
            "dynamic_challenge", sa.Column("initial", sa.Integer(), nullable=True)
        )
    if "minimum" not in columns:
        op.add_column(
            "dynamic_challenge", sa.Column("minimum", sa.Integer(), nullable=True)
        )

    # Copy data from new columns back to old columns
    connection = op.get_bind()
    url = str(connection.engine.url)
    if url.startswith("postgres"):
        connection.execute(
            sa.text(
                """
                UPDATE dynamic_challenge
                SET initial = dynamic_initial,
                    minimum = dynamic_minimum,
                    decay = dynamic_decay,
                    function = dynamic_function
            """
            )
        )
    else:
        connection.execute(
            sa.text(
                """
                UPDATE dynamic_challenge
                SET initial = dynamic_initial,
                    minimum = dynamic_minimum,
                    decay = dynamic_decay,
                    `function` = dynamic_function
            """
            )
        )

    # Drop new columns
    if "dynamic_function" in columns:
        op.drop_column("dynamic_challenge", "dynamic_function")
    if "dynamic_decay" in columns:
        op.drop_column("dynamic_challenge", "dynamic_decay")
    if "dynamic_minimum" in columns:
        op.drop_column("dynamic_challenge", "dynamic_minimum")
    if "dynamic_initial" in columns:
        op.drop_column("dynamic_challenge", "dynamic_initial")
