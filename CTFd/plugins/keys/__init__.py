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
    def compare(chal_key_obj, provided):
        saved = chal_key_obj.flag
        data = chal_key_obj.data

        if len(saved) != len(provided):
            return False
        result = 0

        if data == "case_insensitive":
            for x, y in zip(saved.lower(), provided.lower()):
                result |= ord(x) ^ ord(y)
        else:
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
    def compare(chal_key_obj, provided):
        saved = chal_key_obj.flag
        data = chal_key_obj.data

        if data == "case_insensitive":
            res = re.match(saved, provided, re.IGNORECASE)
        else:
            res = re.match(saved, provided)

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
