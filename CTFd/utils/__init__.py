import mistune
import six
from flask import current_app as app
from CTFd.cache import cache

string_types = six.string_types
text_type = six.text_type
binary_type = six.binary_type
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
            truth_dict = {'true': True, 'false': False}
            return truth_dict.get(value.lower(), value)


def get_config(key, default=None):
    value = _get_config(key)
    return default if value is None else value


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


from CTFd.models import (  # noqa: E402
    db,
    Configs
)
