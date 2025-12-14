"""Add cascading delete to dynamic challenges

Revision ID: b37fb68807ea
Revises:
Create Date: 2020-05-06 12:21:39.373983

"""
import sqlalchemy

revision = "b37fb68807ea"
down_revision = None
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

def upgrade(op=None):
    bind = op.get_bind()
    url = str(bind.engine.url)

    try:
        if url.startswith("mysql"):
            mysql_op_drop_constraint(
                op, "dynamic_challenge_ibfk_1", "dynamic_challenge", type_="foreignkey"
            )
        elif url.startswith("postgres"):
            op.drop_constraint(
                "dynamic_challenge_id_fkey", "dynamic_challenge", type_="foreignkey"
            )
    except sqlalchemy.exc.InternalError as e:
        print(str(e))

    try:
        op.create_foreign_key(
            None, "dynamic_challenge", "challenges", ["id"], ["id"], ondelete="CASCADE"
        )
    except sqlalchemy.exc.InternalError as e:
        print(str(e))


def downgrade(op=None):
    bind = op.get_bind()
    url = str(bind.engine.url)
    try:
        if url.startswith("mysql"):
            mysql_op_drop_constraint(
                op, "dynamic_challenge_ibfk_1", "dynamic_challenge", type_="foreignkey"
            )
        elif url.startswith("postgres"):
            op.drop_constraint(
                "dynamic_challenge_id_fkey", "dynamic_challenge", type_="foreignkey"
            )
    except sqlalchemy.exc.InternalError as e:
        print(str(e))

    try:
        op.create_foreign_key(None, "dynamic_challenge", "challenges", ["id"], ["id"])
    except sqlalchemy.exc.InternalError as e:
        print(str(e))
