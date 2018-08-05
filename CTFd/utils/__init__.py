import datetime
import json
import logging
import mistune
import six
from flask import current_app as app, request, redirect, url_for, session, render_template, abort, jsonify
from flask_caching import Cache
from flask_migrate import Migrate, upgrade as migrate_upgrade, stamp as migrate_stamp
from CTFd.models import (
    db,
    Challenges,
    WrongKeys,
    Pages,
    Config,
    Tracking,
    Teams,
    Files
)

if six.PY2:
    text_type = unicode
    binary_type = str
else:
    text_type = str
    binary_type = bytes

cache = Cache()
migrate = Migrate()
markdown = mistune.Markdown()


@cache.memoize()
def get_app_config(key):
    value = app.config.get(key)
    return value


@cache.memoize()
def get_config(key):
    config = Config.query.filter_by(key=key).first()
    if config and config.value:
        value = config.value
        if value and value.isdigit():
            return int(value)
        elif value and isinstance(value, six.string_types):
            if value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False
            else:
                return value
    else:
        set_config(key, None)
        return None


def set_config(key, value):
    config = Config.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Config(key, value)
        db.session.add(config)
    db.session.commit()
    return config
