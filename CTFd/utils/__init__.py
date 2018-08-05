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
def get_config(key, default=None):
    c = Config.query.filter_by(key=key).first()
    if c and c.value:
        value = c.value
        return json.loads(value)
    else:
        return default


def set_config(key, value):
    c = Config.query.filter_by(key=key).first()
    value = json.dumps(value)
    if c:
        c.value = value
    else:
        c = Config(key, value)
        db.session.add(c)
    db.session.commit()
    return c
