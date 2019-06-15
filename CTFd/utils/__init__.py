import mistune
import six
from flask import current_app as app
from CTFd.cache import cache

if six.PY2:
    string_types = (str, unicode)  # noqa: F821
    text_type = unicode  # noqa: F821
    binary_type = str
else:
    string_types = (str,)
    text_type = str
    binary_type = bytes

markdown = mistune.Markdown()


def get_app_config(key, default=None):
    value = app.config.get(key, default)
    return value


@cache.memoize()
def _get_config(key):
    config = Configs.query.filter_by(key=key).first()
    if config and config.value:
        value = config.value
        if value and value.isdigit():
            return int(value)
        elif value and isinstance(value, six.string_types):
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
    cache.delete_memoized(_get_config, key)
    return config


from CTFd.models import db, Configs  # noqa: E402
