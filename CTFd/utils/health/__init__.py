from time import monotonic_ns

from flask import current_app
from sqlalchemy_utils import database_exists

from CTFd.cache import cache, timed_lru_cache


@timed_lru_cache(timeout=30)
def check_database():
    return database_exists(current_app.config["SQLALCHEMY_DATABASE_URI"])


@timed_lru_cache(timeout=30)
def check_config():
    value = monotonic_ns()
    cache.set("healthcheck", value)
    return cache.get("healthcheck") == value
