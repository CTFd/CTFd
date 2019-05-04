"""Add ondelete cascade to foreign keys

Revision ID: b295b033364d
Revises: b5551cd26764
Create Date: 2019-05-03 19:26:57.746887

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'b295b033364d'
down_revision = 'b5551cd26764'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('awards_ibfk_1', 'awards', type_='foreignkey')
    op.drop_constraint('awards_ibfk_2', 'awards', type_='foreignkey')
    op.create_foreign_key('awards_ibfk_1', 'awards', 'teams', ['team_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('awards_ibfk_2', 'awards', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('files_ibfk_1', 'files', type_='foreignkey')
    op.create_foreign_key('files_ibfk_1', 'files', 'challenges', ['challenge_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('flags_ibfk_1', 'flags', type_='foreignkey')
    op.create_foreign_key('flags_ibfk_1', 'flags', 'challenges', ['challenge_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('hints_ibfk_1', 'hints', type_='foreignkey')
    op.create_foreign_key('hints_ibfk_1', 'hints', 'challenges', ['challenge_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('tags_ibfk_1', 'tags', type_='foreignkey')
    op.create_foreign_key('tags_ibfk_1', 'tags', 'challenges', ['challenge_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('team_captain_id', 'teams', type_='foreignkey')
    op.create_foreign_key('team_captain_id', 'teams', 'users', ['captain_id'], ['id'], ondelete='SET NULL')

    op.drop_constraint('tracking_ibfk_1', 'tracking', type_='foreignkey')
    op.create_foreign_key('tracking_ibfk_1', 'tracking', 'users', ['user_id'], ['id'], ondelete='CASCADE')

    op.drop_constraint('unlocks_ibfk_1', 'unlocks', type_='foreignkey')
    op.drop_constraint('unlocks_ibfk_2', 'unlocks', type_='foreignkey')
    op.create_foreign_key('unlocks_ibfk_1', 'unlocks', 'teams', ['team_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('unlocks_ibfk_2', 'unlocks', 'users', ['user_id'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint('unlocks_ibfk_1', 'unlocks', type_='foreignkey')
    op.drop_constraint('unlocks_ibfk_2', 'unlocks', type_='foreignkey')
    op.create_foreign_key('unlocks_ibfk_1', 'unlocks', 'teams', ['team_id'], ['id'])
    op.create_foreign_key('unlocks_ibfk_2', 'unlocks', 'users', ['user_id'], ['id'])

    op.drop_constraint('tracking_ibfk_1', 'tracking', type_='foreignkey')
    op.create_foreign_key('tracking_ibfk_1', 'tracking', 'users', ['user_id'], ['id'])

    op.drop_constraint('team_captain_id', 'teams', type_='foreignkey')
    op.create_foreign_key('team_captain_id', 'teams', 'users', ['captain_id'], ['id'])

    op.drop_constraint('tags_ibfk_1', 'tags', type_='foreignkey')
    op.create_foreign_key('tags_ibfk_1', 'tags', 'challenges', ['challenge_id'], ['id'])

    op.drop_constraint('hints_ibfk_1', 'hints', type_='foreignkey')
    op.create_foreign_key('hints_ibfk_1', 'hints', 'challenges', ['challenge_id'], ['id'])

    op.drop_constraint('flags_ibfk_1', 'flags', type_='foreignkey')
    op.create_foreign_key('flags_ibfk_1', 'flags', 'challenges', ['challenge_id'], ['id'])

    op.drop_constraint('files_ibfk_1', 'files', type_='foreignkey')
    op.create_foreign_key('files_ibfk_1', 'files', 'challenges', ['challenge_id'], ['id'])

    op.drop_constraint('awards_ibfk_1', 'awards', type_='foreignkey')
    op.drop_constraint('awards_ibfk_2', 'awards', type_='foreignkey')
    op.create_foreign_key('awards_ibfk_1', 'awards', 'teams', ['team_id'], ['id'])
    op.create_foreign_key('awards_ibfk_2', 'awards', 'users', ['user_id'], ['id'])
