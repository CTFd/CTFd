from CTFd.plugins import register_plugin_assets_directory

import re
import string
import hmac


class BaseKey(object):
    id = None
    name = None
    templates = {}

    @staticmethod
    def compare(self, saved, provided):
        return True


class CTFdStaticKey(BaseKey):
    id = 0
    name = "static"
    templates = {  # Nunjucks templates used for key editing & viewing
        'create': '/plugins/keys/assets/static/create-static-modal.njk',
        'update': '/plugins/keys/assets/static/edit-static-modal.njk',
    }

    @staticmethod
    def compare(saved, provided):
        if len(saved) != len(provided):
            return False
        result = 0
        for x, y in zip(saved, provided):
            result |= ord(x) ^ ord(y)
        return result == 0


class CTFdRegexKey(BaseKey):
    id = 1
    name = "regex"
    templates = {  # Nunjucks templates used for key editing & viewing
        'create': '/plugins/keys/assets/regex/create-regex-modal.njk',
        'update': '/plugins/keys/assets/regex/edit-regex-modal.njk',
    }

    @staticmethod
    def compare(saved, provided):
        res = re.match(saved, provided, re.IGNORECASE)
        return res and res.group() == provided


KEY_CLASSES = {
    'static': CTFdStaticKey,
    'regex': CTFdRegexKey
}


def get_key_class(class_id):
    cls = KEY_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


def load(app):
    register_plugin_assets_directory(app, base_path='/plugins/keys/assets/')
