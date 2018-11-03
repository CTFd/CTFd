from flask_caching import Cache

cache = Cache()


def clear_config():
    from CTFd.utils import get_config, get_app_config
    cache.delete_memoized(get_config)
    cache.delete_memoized(get_app_config)


def clear_standings():
    from CTFd.utils.scores import get_standings
    cache.delete_memoized(get_standings)
