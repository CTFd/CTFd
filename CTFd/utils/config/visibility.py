from CTFd.utils import get_config
from CTFd.utils.user import authed, is_admin


def challenges_visible():
    v = get_config("challenge_visibility")
    if v == "public":
        return True
    elif v == "private":
        return authed()
    elif v == "admins":
        return is_admin()


def scores_visible():
    v = get_config("score_visibility")
    if v == "public":
        return True
    elif v == "private":
        return authed()
    elif v == "hidden":
        return False
    elif v == "admins":
        return is_admin()


def accounts_visible():
    v = get_config("account_visibility")
    if v == "public":
        return True
    elif v == "private":
        return authed()
    elif v == "admins":
        return is_admin()


def registration_visible():
    v = get_config("registration_visibility")
    if v == "public":
        return True
    elif v == "private":
        return False
