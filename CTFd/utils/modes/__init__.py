from CTFd.utils import get_config, set_config
from CTFd.models import Users, Teams
from flask import url_for

USERS_MODE = 'users'
TEAMS_MODE = 'teams'


def generate_account_url(account_id, admin=False):
    if get_config('user_mode') == USERS_MODE:
        if admin:
            return url_for('admin.users_detail', user_id=account_id)
        else:
            return url_for('users.public', user_id=account_id)
    elif get_config('user_mode') == TEAMS_MODE:
        if admin:
            return url_for('admin.teams_detail', team_id=account_id)
        else:
            return url_for('teams.public', team_id=account_id)


def get_model():
    if get_config('user_mode') == USERS_MODE:
        return Users
    elif get_config('user_mode') == TEAMS_MODE:
        return Teams
