import re
import string
import hmac


class BaseKey(object):
    id = None
    name = None

    @staticmethod
    def compare(self, saved, provided):
        return True

class CTFdStaticKey(BaseKey):
    id = 0
    name = "static"

    @staticmethod
    def compare(saved, provided):
        return hmac.compare_digest(saved.lower(), provided.lower())


class CTFdRegexKey(BaseKey):
    id = 1
    name = "regex"

    @staticmethod
    def compare(saved, provided):
        res = re.match(saved, provided, re.IGNORECASE)
        return res and res.group() == provided


KEY_CLASSES = {
    0 : CTFdStaticKey,
    1 : CTFdRegexKey
}


def get_key_class(class_id):
    cls = KEY_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls