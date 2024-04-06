from functools import lru_cache, wraps
from hashlib import md5
from time import monotonic_ns

from flask import request
from flask_caching import Cache, make_template_fragment_key

cache = Cache()


def timed_lru_cache(timeout: int = 300, maxsize: int = 64, typed: bool = False):
    """
    lru_cache implementation that includes a time based expiry

    Parameters:
    seconds (int): Timeout in seconds to clear the WHOLE cache, default = 5 minutes
    maxsize (int): Maximum Size of the Cache
    typed (bool): Same value of different type will be a different entry

    Implmentation from https://gist.github.com/Morreski/c1d08a3afa4040815eafd3891e16b945?permalink_comment_id=3437689#gistcomment-3437689
    """

    def wrapper_cache(func):
        func = lru_cache(maxsize=maxsize, typed=typed)(func)
        func.delta = timeout * 10**9
        func.expiration = monotonic_ns() + func.delta

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if monotonic_ns() >= func.expiration:
                func.cache_clear()
                func.expiration = monotonic_ns() + func.delta
            return func(*args, **kwargs)

        wrapped_func.cache_info = func.cache_info
        wrapped_func.cache_clear = func.cache_clear
        return wrapped_func

    return wrapper_cache


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


def make_cache_key_with_query_string(allowed_params=None, query_string_hash=None):
    if allowed_params is None:
        allowed_params = []

    def _make_cache_key_with_query_string(path=None, key_prefix="view/%s/%s"):
        if path is None:
            path = request.endpoint

        if query_string_hash:
            args_hash = query_string_hash
        else:
            args_hash = calculate_param_hash(
                params=tuple(request.args.items(multi=True)),
                allowed_params=allowed_params,
            )
        cache_key = key_prefix % (path, args_hash)
        return cache_key

    return _make_cache_key_with_query_string


def calculate_param_hash(params, allowed_params=None):
    # Copied from Flask-Caching but modified to allow only accepted parameters
    if allowed_params:
        args_as_sorted_tuple = tuple(
            sorted(pair for pair in params if pair[0] in allowed_params)
        )
    else:
        args_as_sorted_tuple = tuple(sorted(pair for pair in params))
    args_hash = md5(str(args_as_sorted_tuple).encode()).hexdigest()  # nosec B303
    return args_hash


def clear_config():
    from CTFd.utils import _get_config, get_app_config

    cache.delete_memoized(_get_config)
    cache.delete_memoized(get_app_config)


def clear_standings():
    from CTFd.api import api
    from CTFd.api.v1.scoreboard import ScoreboardDetail, ScoreboardList
    from CTFd.constants.static import CacheKeys
    from CTFd.models import Brackets, Teams, Users  # noqa: I001
    from CTFd.utils.scores import get_standings, get_team_standings, get_user_standings
    from CTFd.utils.user import (
        get_team_place,
        get_team_score,
        get_user_place,
        get_user_score,
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
    cache.delete(make_cache_key(path=api.name + "." + ScoreboardList.endpoint))
    cache.delete(make_cache_key(path=api.name + "." + ScoreboardDetail.endpoint))
    cache.delete_memoized(ScoreboardList.get)
    cache.delete_memoized(ScoreboardDetail.get)

    # Clear out scoreboard detail
    keys = [()]  # Empty tuple to handle case with no parameters
    brackets = Brackets.query.all()
    for bracket in brackets:
        keys.append((("bracket_id", str(bracket.id)),))
    for k in keys:
        cache_func = make_cache_key_with_query_string(
            query_string_hash=calculate_param_hash(params=k)
        )
        cache_key = cache_func(path=api.name + "." + ScoreboardDetail.endpoint)
        cache.delete(cache_key)

    # Clear out scoreboard templates
    cache.delete(make_template_fragment_key(CacheKeys.PUBLIC_SCOREBOARD_TABLE))


def clear_challenges():
    from CTFd.utils.challenges import get_all_challenges  # noqa: I001
    from CTFd.utils.challenges import (
        get_solve_counts_for_challenges,
        get_solve_ids_for_user_id,
        get_solves_for_challenge_id,
    )

    cache.delete_memoized(get_all_challenges)
    cache.delete_memoized(get_solves_for_challenge_id)
    cache.delete_memoized(get_solve_ids_for_user_id)
    cache.delete_memoized(get_solve_counts_for_challenges)


def clear_pages():
    from CTFd.utils.config.pages import get_page, get_pages

    cache.delete_memoized(get_pages)
    cache.delete_memoized(get_page)


def clear_user_recent_ips(user_id):
    from CTFd.utils.user import get_user_recent_ips

    cache.delete_memoized(get_user_recent_ips, user_id=user_id)


def clear_user_session(user_id):
    from CTFd.utils.user import (  # noqa: I001
        get_user_attrs,
        get_user_place,
        get_user_recent_ips,
        get_user_score,
    )

    cache.delete_memoized(get_user_attrs, user_id=user_id)
    cache.delete_memoized(get_user_place, user_id=user_id)
    cache.delete_memoized(get_user_score, user_id=user_id)
    cache.delete_memoized(get_user_recent_ips, user_id=user_id)


def clear_all_user_sessions():
    from CTFd.utils.user import (  # noqa: I001
        get_user_attrs,
        get_user_place,
        get_user_recent_ips,
        get_user_score,
    )

    cache.delete_memoized(get_user_attrs)
    cache.delete_memoized(get_user_place)
    cache.delete_memoized(get_user_score)
    cache.delete_memoized(get_user_recent_ips)


def clear_team_session(team_id):
    from CTFd.utils.user import get_team_attrs, get_team_place, get_team_score

    cache.delete_memoized(get_team_attrs, team_id=team_id)
    cache.delete_memoized(get_team_place, team_id=team_id)
    cache.delete_memoized(get_team_score, team_id=team_id)


def clear_all_team_sessions():
    from CTFd.utils.user import get_team_attrs, get_team_place, get_team_score

    cache.delete_memoized(get_team_attrs)
    cache.delete_memoized(get_team_place)
    cache.delete_memoized(get_team_score)
