from flask_caching import Cache

cache = Cache()


def clear_config():
    from CTFd.utils import _get_config, get_app_config
    cache.delete_memoized(_get_config)
    cache.delete_memoized(get_app_config)


def clear_standings():
    from CTFd.utils.scores import get_standings
    cache.delete_memoized(get_standings)


def clear_pages():
    from CTFd.utils.config.pages import get_page, get_pages
    cache.delete_memoized(get_pages)
    cache.delete_memoized(get_page)
