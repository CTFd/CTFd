from flask import request
from flask_caching import Cache
from jinja2 import BytecodeCache

cache = Cache()


class RedisJinjaBytecodeCache(BytecodeCache):
    """
    Jinja bytecode cache based on Flask-Caching
    """

    def load_bytecode(self, bucket):
        key = make_cache_key(path=bucket.key, key_prefix="template/%s")
        bc = cache.get(key)
        if bc:
            bucket.bytecode_from_string(bc)

    def dump_bytecode(self, bucket):
        key = make_cache_key(path=bucket.key, key_prefix="template/%s")
        cache.set(key=key, value=bucket.bytecode_to_string(), timeout=300)


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
    from CTFd.utils.scores import get_standings, get_team_standings, get_user_standings
    from CTFd.api.v1.scoreboard import ScoreboardDetail, ScoreboardList
    from CTFd.api import api

    cache.delete_memoized(get_standings)
    cache.delete_memoized(get_team_standings)
    cache.delete_memoized(get_user_standings)
    cache.delete(make_cache_key(path="scoreboard.listing"))
    cache.delete(make_cache_key(path=api.name + "." + ScoreboardList.endpoint))
    cache.delete(make_cache_key(path=api.name + "." + ScoreboardDetail.endpoint))
    cache.delete_memoized(ScoreboardList.get)


def clear_pages():
    from CTFd.utils.config.pages import get_page, get_pages

    cache.delete_memoized(get_pages)
    cache.delete_memoized(get_page)
