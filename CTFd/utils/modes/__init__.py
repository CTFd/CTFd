from flask import url_for
from flask_babel import ngettext

from CTFd.models import Teams, Users
from CTFd.utils import get_config

# TODO: Replace these constants with the UserModeTypes enum
USERS_MODE = "users"
TEAMS_MODE = "teams"


def generate_account_url(account_id, admin=False):
    if get_config("user_mode") == USERS_MODE:
        if admin:
            return url_for("admin.users_detail", user_id=account_id)
        else:
            return url_for("users.public", user_id=account_id)
    elif get_config("user_mode") == TEAMS_MODE:
        if admin:
            return url_for("admin.teams_detail", team_id=account_id)
        else:
            return url_for("teams.public", team_id=account_id)


def get_model():
    if get_config("user_mode") == USERS_MODE:
        return Users
    elif get_config("user_mode") == TEAMS_MODE:
        return Teams


def get_mode_as_word(plural=False, capitalize=False):
    count = 2 if plural else 1
    if get_config("user_mode") == USERS_MODE:
        word = ngettext("user", "users", count)
    else:
        word = ngettext("team", "teams", count)

    if capitalize:
        word = word.title()
    return word
