"""Adds challenge types and uses keys table

Revision ID: 87733981ca0e
Revises: cb3cfcc47e2f
Create Date: 2017-02-04 14:50:16.999303

"""
from CTFd.models import db, Challenges, Keys
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text, table, column
from sqlalchemy.orm import sessionmaker
import json


# revision identifiers, used by Alembic.
revision = '87733981ca0e'
down_revision = 'cb3cfcc47e2f'
branch_labels = None
depends_on = None

keys_table = table('keys',
    column('id', db.Integer),
    column('chal', db.Integer),
    column('type', db.Integer),
    column('flag', db.Text)
)

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    ## Copy over flags data to Keys table
    # print("Getting bind...")
    conn = op.get_bind()

    # print("Executing: SELECT id, flags from challenges")
    res = conn.execute(text("SELECT id, flags from challenges"))
    results = res.fetchall()

    # print("There are {} results".format(len(results)))
    new_keys = []
    # print("Processing existing flags")
    for r in results:
        if r[1]: ## Check if flags are NULL
            data = json.loads(r[1])
            for old_keys in data:
                new_keys.append({'chal':r[0], 'flag':old_keys.get('flag'), 'type':old_keys.get('type')})
    if new_keys:
        ## Base CTFd databases actually already insert into Keys but the database does not make use of them
        ## This prevents duplicate entries of keys
        # print("Executing: TRUNCATE keys")
        conn.execute(text("TRUNCATE `keys`"))

        print("Bulk inserting the keys")
        op.bulk_insert(keys_table, new_keys)

    ## Add type column to challenges
    # print("Adding type column to challenges")
    op.add_column('challenges', sa.Column('type', sa.Integer(), nullable=True, default=0))

    ## Set all NULLs to 0
    # print("Setting all NULLs to 0")
    conn.execute("UPDATE challenges set type=0 WHERE type IS NULL")

    ## Drop flags from challenges
    # print("Dropping flags column from challenges")
    try:
        op.drop_column('challenges', 'flags')
    except sa.exc.OperationalError:
        print("Failed to drop flags. Likely due to SQLite")


    # print("Finished")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    # print("Getting bind...")
    conn = op.get_bind()

    # print("Adding flags column back to challenges table")
    op.add_column('challenges', sa.Column('flags', sa.TEXT(), nullable=True))

    # print("Dropping type column from challenges table")
    op.drop_column('challenges', 'type')

    # print("Executing: SELECT id, flags from challenges")
    res = conn.execute("SELECT id, flags from challenges")
    results = res.fetchall()

    # print("There are {} results".format(len(results)))
    for chal_id in results:
        new_keys = Keys.query.filter_by(chal=chal_id[0]).all()
        old_flags = []
        for new_key in new_keys:
            flag_dict = {'flag': new_key.flag, 'type': new_key.type}
            old_flags.append(flag_dict)
        old_flags =json.dumps(old_flags)
        # print("Updating challenge {} to insert {}".format(chal_id[0], flag_dict))
        conn.execute(text('UPDATE challenges SET flags=:flags WHERE id=:id'), id=chal_id[0], flags=old_flags)

    # print("Finished")
    # ### end Alembic commands ###
