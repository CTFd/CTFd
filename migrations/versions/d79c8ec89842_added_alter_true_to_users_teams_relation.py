"""Added alter=True to users-teams relation

Revision ID: d79c8ec89842
Revises: 1093835a1051
Create Date: 2020-05-13 11:18:02.894033

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "d79c8ec89842"
down_revision = "1093835a1051"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith("postgres"):
        op.drop_constraint("users_team_id_fkey", "users", type_="foreignkey")
    elif url.startswith("mysql"):
        op.drop_constraint("users_ibfk_1", "users", type_="foreignkey")
    op.create_foreign_key(
        "users_team_id_fkey",
        "users",
        "teams",
        ["team_id"],
        ["id"],
        ondelete="CASCADE",
        use_alter=True,
    )


def downgrade():
    op.drop_constraint("users_team_id_fkey", "users", type_="foreignkey")
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith("postgres"):

        op.create_foreign_key(
            "users_team_id_fkey1", "users", "teams", ["team_id"], ["id"]
        )
    elif url.startswith("mysql"):
        op.create_foreign_key("users_ibfk_1", "users", "teams", ["team_id"], ["id"])
