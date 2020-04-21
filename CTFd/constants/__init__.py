from enum import Enum
from flask import current_app

JS_ENUMS = {}


class RawEnum(Enum):
    def __str__(self):
        return str(self._value_)

    @classmethod
    def keys(cls):
        return list(cls.__members__.keys())

    @classmethod
    def values(cls):
        return list(cls.__members__.values())

    @classmethod
    def test(cls, value):
        try:
            return bool(cls(value))
        except ValueError:
            return False


def JSEnum(cls):
    if cls.__name__ not in JS_ENUMS:
        JS_ENUMS[cls.__name__] = dict(cls.__members__)
    else:
        raise KeyError("{} was already defined as a JSEnum".format(cls.__name__))
    return cls


def JinjaEnum(cls):
    if cls.__name__ not in current_app.jinja_env.globals:
        current_app.jinja_env.globals[cls.__name__] = cls
    else:
        raise KeyError("{} was already defined as a JinjaEnum".format(cls.__name__))
    return cls
