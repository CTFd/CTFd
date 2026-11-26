"""Allow challenges to belong to many modules

Revision ID: c7d2e4f6a8b1
Revises: a3e1c5d7b9f2
Create Date: 2026-11-26 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "c7d2e4f6a8b1"
down_revision = "a3e1c5d7b9f2"
branch_labels = None
depends_on = None


def _module_id_fk_name(bind):
    for fk in sa.inspect(bind).get_foreign_keys("challenges"):
        if fk["constrained_columns"] == ["module_id"]:
            return fk["name"]
    return None


def _has_module_id_column(bind):
    columns = sa.inspect(bind).get_columns("challenges")
    return any(c["name"] == "module_id" for c in columns)


def upgrade():
    op.create_table(
        "module_challenges",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("module_id", sa.Integer(), nullable=False),
        sa.Column("challenge_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["challenge_id"], ["challenges.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("module_id", "challenge_id", name="uq_module_challenge"),
    )

    bind = op.get_bind()
    if not _has_module_id_column(bind):
        return

    op.execute(
        "INSERT INTO module_challenges (module_id, challenge_id) "
        "SELECT module_id, id FROM challenges WHERE module_id IS NOT NULL"
    )

    # don't drop the column on sqlite
    if bind.dialect.name == "sqlite":
        return

    fk_name = _module_id_fk_name(bind)
    if fk_name:
        op.drop_constraint(fk_name, "challenges", type_="foreignkey")
    op.drop_column("challenges", "module_id")


def downgrade():
    bind = op.get_bind()
    if not _has_module_id_column(bind):
        op.add_column("challenges", sa.Column("module_id", sa.Integer(), nullable=True))
        if bind.dialect.name != "sqlite":
            op.create_foreign_key(
                None,
                "challenges",
                "modules",
                ["module_id"],
                ["id"],
                ondelete="SET NULL",
            )

    op.execute(
        "UPDATE challenges SET module_id = ("
        "SELECT MIN(module_challenges.module_id) FROM module_challenges "
        "WHERE module_challenges.challenge_id = challenges.id)"
    )
    op.drop_table("module_challenges")
