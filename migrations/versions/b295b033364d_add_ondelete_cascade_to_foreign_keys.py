"""Add ondelete cascade to foreign keys

Revision ID: b295b033364d
Revises: b5551cd26764
Create Date: 2019-05-03 19:26:57.746887

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "b295b033364d"
down_revision = "b5551cd26764"
branch_labels = None
depends_on = None

# Helper function to handle the drop constraint
def mysql_op_drop_constraint(op, name, table_name, type_):
    """
    Attempts to drop a constraint
    If the default constraint name format is used (`table_ibfk_number`)
    it will try to fix know problems related to MariaDB 12.1 and above
    https://mariadb.org/per-table-unique-foreign-key-constraint-names-new-feature-in-mariadb-12-1/
    """
    # If default contraint name is used
    if name.startswith(table_name + '_ibfk_'):
        # Try to run the constraint drop operation as normal
        try:
            op.drop_constraint(name, table_name, type_=type_)
            return

        # Monitor for errors
        except Exception as e:
            # Inspect the error
            if hasattr(e, 'orig') and hasattr(e.orig, 'args'):
                error_code = e.orig.args[0]

                # If the error is "constraint not found" (1091)
                if error_code == 1091:
                    # This may mean that a MariaDB 12.1 or above is used, so try again with the new default naming
                    op.drop_constraint(name.split('_ibfk_', 1)[1], table_name, type_=type_)
                    return    
            # Re-raise any other unexpected operational error
            raise
    else:
        # Try to run the constraint drop operation as normal
        op.drop_constraint(name, table_name, type_=type_)

def upgrade():
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith("mysql"):
        mysql_op_drop_constraint(op, "awards_ibfk_1", "awards", type_="foreignkey")
        mysql_op_drop_constraint(op, "awards_ibfk_2", "awards", type_="foreignkey")
        op.create_foreign_key(
            "awards_ibfk_1", "awards", "teams", ["team_id"], ["id"], ondelete="CASCADE"
        )
        op.create_foreign_key(
            "awards_ibfk_2", "awards", "users", ["user_id"], ["id"], ondelete="CASCADE"
        )

        mysql_op_drop_constraint(op, "files_ibfk_1", "files", type_="foreignkey")
        op.create_foreign_key(
            "files_ibfk_1",
            "files",
            "challenges",
            ["challenge_id"],
            ["id"],
            ondelete="CASCADE",
        )

        mysql_op_drop_constraint(op, "flags_ibfk_1", "flags", type_="foreignkey")
        op.create_foreign_key(
            "flags_ibfk_1",
            "flags",
            "challenges",
            ["challenge_id"],
            ["id"],
            ondelete="CASCADE",
        )

        mysql_op_drop_constraint(op, "hints_ibfk_1", "hints", type_="foreignkey")
        op.create_foreign_key(
            "hints_ibfk_1",
            "hints",
            "challenges",
            ["challenge_id"],
            ["id"],
            ondelete="CASCADE",
        )

        mysql_op_drop_constraint(op, "tags_ibfk_1", "tags", type_="foreignkey")
        op.create_foreign_key(
            "tags_ibfk_1",
            "tags",
            "challenges",
            ["challenge_id"],
            ["id"],
            ondelete="CASCADE",
        )

        mysql_op_drop_constraint(op, "team_captain_id", "teams", type_="foreignkey")
        op.create_foreign_key(
            "team_captain_id",
            "teams",
            "users",
            ["captain_id"],
            ["id"],
            ondelete="SET NULL",
        )

        mysql_op_drop_constraint(op, "tracking_ibfk_1", "tracking", type_="foreignkey")
        op.create_foreign_key(
            "tracking_ibfk_1",
            "tracking",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

        mysql_op_drop_constraint(op, "unlocks_ibfk_1", "unlocks", type_="foreignkey")
        mysql_op_drop_constraint(op, "unlocks_ibfk_2", "unlocks", type_="foreignkey")
        op.create_foreign_key(
            "unlocks_ibfk_1",
            "unlocks",
            "teams",
            ["team_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_foreign_key(
            "unlocks_ibfk_2",
            "unlocks",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )
    elif url.startswith("postgres"):
        op.drop_constraint("awards_team_id_fkey", "awards", type_="foreignkey")
        op.drop_constraint("awards_user_id_fkey", "awards", type_="foreignkey")
        op.create_foreign_key(
            "awards_team_id_fkey",
            "awards",
            "teams",
            ["team_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_foreign_key(
            "awards_user_id_fkey",
            "awards",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

        op.drop_constraint("files_challenge_id_fkey", "files", type_="foreignkey")
        op.create_foreign_key(
            "files_challenge_id_fkey",
            "files",
            "challenges",
            ["challenge_id"],
            ["id"],
            ondelete="CASCADE",
        )

        op.drop_constraint("flags_challenge_id_fkey", "flags", type_="foreignkey")
        op.create_foreign_key(
            "flags_challenge_id_fkey",
            "flags",
            "challenges",
            ["challenge_id"],
            ["id"],
            ondelete="CASCADE",
        )

        op.drop_constraint("hints_challenge_id_fkey", "hints", type_="foreignkey")
        op.create_foreign_key(
            "hints_challenge_id_fkey",
            "hints",
            "challenges",
            ["challenge_id"],
            ["id"],
            ondelete="CASCADE",
        )

        op.drop_constraint("tags_challenge_id_fkey", "tags", type_="foreignkey")
        op.create_foreign_key(
            "tags_challenge_id_fkey",
            "tags",
            "challenges",
            ["challenge_id"],
            ["id"],
            ondelete="CASCADE",
        )

        op.drop_constraint("team_captain_id", "teams", type_="foreignkey")
        op.create_foreign_key(
            "team_captain_id",
            "teams",
            "users",
            ["captain_id"],
            ["id"],
            ondelete="SET NULL",
        )

        op.drop_constraint("tracking_user_id_fkey", "tracking", type_="foreignkey")
        op.create_foreign_key(
            "tracking_user_id_fkey",
            "tracking",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )

        op.drop_constraint("unlocks_team_id_fkey", "unlocks", type_="foreignkey")
        op.drop_constraint("unlocks_user_id_fkey", "unlocks", type_="foreignkey")
        op.create_foreign_key(
            "unlocks_team_id_fkey",
            "unlocks",
            "teams",
            ["team_id"],
            ["id"],
            ondelete="CASCADE",
        )
        op.create_foreign_key(
            "unlocks_user_id_fkey",
            "unlocks",
            "users",
            ["user_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade():
    bind = op.get_bind()
    url = str(bind.engine.url)
    if url.startswith("mysql"):
        op.drop_constraint("unlocks_ibfk_1", "unlocks", type_="foreignkey")
        op.drop_constraint("unlocks_ibfk_2", "unlocks", type_="foreignkey")
        op.create_foreign_key("unlocks_ibfk_1", "unlocks", "teams", ["team_id"], ["id"])
        op.create_foreign_key("unlocks_ibfk_2", "unlocks", "users", ["user_id"], ["id"])

        op.drop_constraint("tracking_ibfk_1", "tracking", type_="foreignkey")
        op.create_foreign_key(
            "tracking_ibfk_1", "tracking", "users", ["user_id"], ["id"]
        )

        op.drop_constraint("team_captain_id", "teams", type_="foreignkey")
        op.create_foreign_key(
            "team_captain_id", "teams", "users", ["captain_id"], ["id"]
        )

        op.drop_constraint("tags_ibfk_1", "tags", type_="foreignkey")
        op.create_foreign_key(
            "tags_ibfk_1", "tags", "challenges", ["challenge_id"], ["id"]
        )

        op.drop_constraint("hints_ibfk_1", "hints", type_="foreignkey")
        op.create_foreign_key(
            "hints_ibfk_1", "hints", "challenges", ["challenge_id"], ["id"]
        )

        op.drop_constraint("flags_ibfk_1", "flags", type_="foreignkey")
        op.create_foreign_key(
            "flags_ibfk_1", "flags", "challenges", ["challenge_id"], ["id"]
        )

        op.drop_constraint("files_ibfk_1", "files", type_="foreignkey")
        op.create_foreign_key(
            "files_ibfk_1", "files", "challenges", ["challenge_id"], ["id"]
        )

        op.drop_constraint("awards_ibfk_1", "awards", type_="foreignkey")
        op.drop_constraint("awards_ibfk_2", "awards", type_="foreignkey")
        op.create_foreign_key("awards_ibfk_1", "awards", "teams", ["team_id"], ["id"])
        op.create_foreign_key("awards_ibfk_2", "awards", "users", ["user_id"], ["id"])
    elif url.startswith("postgres"):
        op.drop_constraint("unlocks_team_id_fkey", "unlocks", type_="foreignkey")
        op.drop_constraint("unlocks_user_id_fkey", "unlocks", type_="foreignkey")
        op.create_foreign_key(
            "unlocks_team_id_fkey", "unlocks", "teams", ["team_id"], ["id"]
        )
        op.create_foreign_key(
            "unlocks_user_id_fkey", "unlocks", "users", ["user_id"], ["id"]
        )

        op.drop_constraint("tracking_user_id_fkey", "tracking", type_="foreignkey")
        op.create_foreign_key(
            "tracking_user_id_fkey", "tracking", "users", ["user_id"], ["id"]
        )

        op.drop_constraint("team_captain_id", "teams", type_="foreignkey")
        op.create_foreign_key(
            "team_captain_id", "teams", "users", ["captain_id"], ["id"]
        )

        op.drop_constraint("tags_challenge_id_fkey", "tags", type_="foreignkey")
        op.create_foreign_key(
            "tags_challenge_id_fkey", "tags", "challenges", ["challenge_id"], ["id"]
        )

        op.drop_constraint("hints_challenge_id_fkey", "hints", type_="foreignkey")
        op.create_foreign_key(
            "hints_challenge_id_fkey", "hints", "challenges", ["challenge_id"], ["id"]
        )

        op.drop_constraint("flags_challenge_id_fkey", "flags", type_="foreignkey")
        op.create_foreign_key(
            "flags_challenge_id_fkey", "flags", "challenges", ["challenge_id"], ["id"]
        )

        op.drop_constraint("files_challenge_id_fkey", "files", type_="foreignkey")
        op.create_foreign_key(
            "files_challenge_id_fkey", "files", "challenges", ["challenge_id"], ["id"]
        )

        op.drop_constraint("awards_team_id_fkey", "awards", type_="foreignkey")
        op.drop_constraint("awards_user_id_fkey", "awards", type_="foreignkey")
        op.create_foreign_key(
            "awards_team_id_fkey", "awards", "teams", ["team_id"], ["id"]
        )
        op.create_foreign_key(
            "awards_user_id_fkey", "awards", "users", ["user_id"], ["id"]
        )
