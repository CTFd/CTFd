import functools

from flask import abort

from CTFd.utils import get_config
from CTFd.utils.modes import TEAMS_MODE, USERS_MODE


def require_team_mode(f):
    @functools.wraps(f)
    def _require_team_mode(*args, **kwargs):
        if get_config("user_mode") == USERS_MODE:
            abort(404)
        return f(*args, **kwargs)

    return _require_team_mode


def require_user_mode(f):
    @functools.wraps(f)
    def _require_user_mode(*args, **kwargs):
        if get_config("user_mode") == TEAMS_MODE:
            abort(404)
        return f(*args, **kwargs)

    return _require_user_mode
