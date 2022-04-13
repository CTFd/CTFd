import json
from enum import Enum

import cmarkgfm
from cmarkgfm.cmark import Options
from flask import current_app as app

# isort:imports-firstparty
from CTFd.cache import cache
from CTFd.models import Configs, db

string_types = (str,)
text_type = str
binary_type = bytes


def markdown(md):
    return cmarkgfm.markdown_to_html_with_extensions(
        md,
        extensions=["autolink", "table", "strikethrough"],
        options=Options.CMARK_OPT_UNSAFE,
    )


def get_app_config(key, default=None):
    value = app.config.get(key, default)
    return value


@cache.memoize()
def _get_asset_json(path):
    with open(path) as f:
        return json.loads(f.read())


def get_asset_json(path):
    # Ignore caching if we are in debug mode
    if app.debug:
        return _get_asset_json.__wrapped__(path)
    return _get_asset_json(path)


@cache.memoize()
def _get_config(key):
    config = db.session.execute(
        Configs.__table__.select().where(Configs.key == key)
    ).fetchone()
    if config and config.value:
        value = config.value
        if value and value.isdigit():
            return int(value)
        elif value and isinstance(value, string_types):
            if value.lower() == "true":
                return True
            elif value.lower() == "false":
                return False
            else:
                return value
    # Flask-Caching is unable to roundtrip a value of None.
    # Return an exception so that we can still cache and avoid the db hit
    return KeyError


def get_config(key, default=None):
    # Convert enums to raw string values to cache better
    if isinstance(key, Enum):
        key = str(key)

    value = _get_config(key)
    if value is KeyError:
        return default
    else:
        return value


def set_config(key, value):
    config = Configs.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Configs(key=key, value=value)
        db.session.add(config)
    db.session.commit()

    # Convert enums to raw string values to cache better
    if isinstance(key, Enum):
        key = str(key)

    cache.delete_memoized(_get_config, key)
    return config


def import_in_progress():
    import_status = cache.get(key="import_status")
    import_error = cache.get(key="import_error")
    if import_error:
        return False
    elif import_status:
        return True
    else:
        return False
