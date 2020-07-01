from flask import request
from flask_caching import Cache

cache = Cache()


def make_cache_key(path=None, key_prefix="view/%s"):
    """
    This function mostly emulates Flask-Caching's `make_cache_key` function so we can delete cached api responses.
    Over time this function may be replaced with a cleaner custom cache implementation.
    :param path:
    :param key_prefix:
    :return:
    """
    if path is None:
        path = request.endpoint
    cache_key = key_prefix % path
    return cache_key


def clear_config():
    from CTFd.utils import _get_config, get_app_config

    cache.delete_memoized(_get_config)
    cache.delete_memoized(get_app_config)


def clear_standings():
    from CTFd.models import Users, Teams
    from CTFd.utils.scores import get_standings, get_team_standings, get_user_standings
    from CTFd.api.v1.scoreboard import ScoreboardDetail, ScoreboardList
    from CTFd.api import api
    from CTFd.utils.user import (
        get_user_score,
        get_user_place,
        get_team_score,
        get_team_place,
    )

    # Clear out the bulk standings functions
    cache.delete_memoized(get_standings)
    cache.delete_memoized(get_team_standings)
    cache.delete_memoized(get_user_standings)

    # Clear out the individual helpers for accessing score via the model
    cache.delete_memoized(Users.get_score)
    cache.delete_memoized(Users.get_place)
    cache.delete_memoized(Teams.get_score)
    cache.delete_memoized(Teams.get_place)

    # Clear the Jinja Attrs constants
    cache.delete_memoized(get_user_score)
    cache.delete_memoized(get_user_place)
    cache.delete_memoized(get_team_score)
    cache.delete_memoized(get_team_place)

    # Clear out HTTP request responses
    cache.delete(make_cache_key(path="scoreboard.listing"))
    cache.delete(make_cache_key(path=api.name + "." + ScoreboardList.endpoint))
    cache.delete(make_cache_key(path=api.name + "." + ScoreboardDetail.endpoint))
    cache.delete_memoized(ScoreboardList.get)


def clear_pages():
    from CTFd.utils.config.pages import get_page, get_pages

    cache.delete_memoized(get_pages)
    cache.delete_memoized(get_page)


def clear_user_recent_ips(user_id):
    from CTFd.utils.user import get_user_recent_ips

    cache.delete_memoized(get_user_recent_ips, user_id=user_id)


def clear_user_session(user_id):
    from CTFd.utils.user import get_user_attrs

    cache.delete_memoized(get_user_attrs, user_id=user_id)


def clear_all_user_sessions():
    from CTFd.utils.user import get_user_attrs

    cache.delete_memoized(get_user_attrs)


def clear_team_session(team_id):
    from CTFd.utils.user import get_team_attrs

    cache.delete_memoized(get_team_attrs, team_id=team_id)


def clear_all_team_sessions():
    from CTFd.utils.user import get_team_attrs

    cache.delete_memoized(get_team_attrs)
