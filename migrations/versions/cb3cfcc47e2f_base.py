"""Base 1.0.0 CTFd database

Revision ID: cb3cfcc47e2f
Revises:
Create Date: 2017-01-17 15:39:42.804290

"""
from CTFd import create_app
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cb3cfcc47e2f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('challenges',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('flags', sa.Text(), nullable=True),
    sa.Column('hidden', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('config',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('key', sa.Text(), nullable=True),
    sa.Column('value', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('containers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('buildfile', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('pages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('route', sa.String(length=80), nullable=True),
    sa.Column('html', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('route')
    )

    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('website', sa.String(length=128), nullable=True),
    sa.Column('affiliation', sa.String(length=128), nullable=True),
    sa.Column('country', sa.String(length=32), nullable=True),
    sa.Column('bracket', sa.String(length=32), nullable=True),
    sa.Column('banned', sa.Boolean(), nullable=True),
    sa.Column('verified', sa.Boolean(), nullable=True),
    sa.Column('admin', sa.Boolean(), nullable=True),
    sa.Column('joined', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('name')
    )

    op.create_table('awards',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('teamid', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('icon', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['teamid'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('files',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chal', sa.Integer(), nullable=True),
    sa.Column('location', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['chal'], ['challenges.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('keys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chal', sa.Integer(), nullable=True),
    sa.Column('key_type', sa.Integer(), nullable=True),
    sa.Column('flag', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['chal'], ['challenges.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('solves',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chalid', sa.Integer(), nullable=True),
    sa.Column('teamid', sa.Integer(), nullable=True),
    sa.Column('ip', sa.Integer(), nullable=True),
    sa.Column('flag', sa.Text(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['chalid'], ['challenges.id'], ),
    sa.ForeignKeyConstraint(['teamid'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('chalid', 'teamid')
    )

    op.create_table('tags',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chal', sa.Integer(), nullable=True),
    sa.Column('tag', sa.String(length=80), nullable=True),
    sa.ForeignKeyConstraint(['chal'], ['challenges.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('tracking',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip', sa.BigInteger(), nullable=True),
    sa.Column('team', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['team'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )

    op.create_table('wrong_keys',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chalid', sa.Integer(), nullable=True),
    sa.Column('teamid', sa.Integer(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('flag', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['chalid'], ['challenges.id'], ),
    sa.ForeignKeyConstraint(['teamid'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('wrong_keys')
    op.drop_table('tracking')
    op.drop_table('tags')
    op.drop_table('solves')
    op.drop_table('keys')
    op.drop_table('files')
    op.drop_table('awards')
    op.drop_table('teams')
    op.drop_table('pages')
    op.drop_table('containers')
    op.drop_table('config')
    op.drop_table('challenges')
    # ### end Alembic commands ###
