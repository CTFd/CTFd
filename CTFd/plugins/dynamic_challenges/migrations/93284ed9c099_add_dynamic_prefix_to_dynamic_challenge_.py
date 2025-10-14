"""Add dynamic prefix to dynamic_challenge table

Revision ID: 93284ed9c099
Revises: eb68f277ab61
Create Date: 2025-10-10 02:07:16.055798

"""
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "93284ed9c099"
down_revision = "eb68f277ab61"
branch_labels = None
depends_on = None


def upgrade(op=None):
    # Add new columns with dynamic_ prefix
    op.add_column(
        "dynamic_challenge", sa.Column("dynamic_initial", sa.Integer(), nullable=True)
    )
    op.add_column(
        "dynamic_challenge", sa.Column("dynamic_minimum", sa.Integer(), nullable=True)
    )
    op.add_column(
        "dynamic_challenge", sa.Column("dynamic_decay", sa.Integer(), nullable=True)
    )
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
    op.drop_column("dynamic_challenge", "minimum")
    op.drop_column("dynamic_challenge", "initial")
    op.drop_column("dynamic_challenge", "function")
    op.drop_column("dynamic_challenge", "decay")


def downgrade(op=None):
    # Add old columns back
    op.add_column("dynamic_challenge", sa.Column("decay", sa.Integer(), nullable=True))
    op.add_column(
        "dynamic_challenge", sa.Column("function", sa.String(length=32), nullable=True)
    )
    op.add_column(
        "dynamic_challenge", sa.Column("initial", sa.Integer(), nullable=True)
    )
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
    op.drop_column("dynamic_challenge", "dynamic_function")
    op.drop_column("dynamic_challenge", "dynamic_decay")
    op.drop_column("dynamic_challenge", "dynamic_minimum")
    op.drop_column("dynamic_challenge", "dynamic_initial")
