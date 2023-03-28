from time import time

from flask import current_app
from sqlalchemy_utils import database_exists

from CTFd.cache import cache, timed_lru_cache


@timed_lru_cache(timeout=30)
def check_database():
    return database_exists(current_app.config["SQLALCHEMY_DATABASE_URI"])


@timed_lru_cache(timeout=30)
def check_config():
    key = "healthcheck"
    value = round(time() / 5) * 5
    cache.set(key, value)
    return cache.get(key) == value
