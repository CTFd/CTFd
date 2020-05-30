from enum import Enum

from flask import current_app

JS_ENUMS = {}


class RawEnum(Enum):
    """
    This is a customized enum class which should be used with a mixin.
    The mixin should define the types of each member.

    For example:

    class Colors(str, RawEnum):
        RED = "red"
        GREEN = "green"
        BLUE = "blue"
    """

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
    """
    This is a decorator used to gather all Enums which should be shared with
    the CTFd front end. The JS_Enums dictionary can be taken be a script and
    compiled into a JavaScript file for use by frontend assets. JS_Enums
    should not be passed directly into Jinja. A JinjaEnum is better for that.
    """
    if cls.__name__ not in JS_ENUMS:
        JS_ENUMS[cls.__name__] = dict(cls.__members__)
    else:
        raise KeyError("{} was already defined as a JSEnum".format(cls.__name__))
    return cls


def JinjaEnum(cls):
    """
    This is a decorator used to inject the decorated Enum into Jinja globals
    which allows you to access it from the front end. If you need to access
    an Enum from JS, a better tool to use is the JSEnum decorator.
    """
    if cls.__name__ not in current_app.jinja_env.globals:
        current_app.jinja_env.globals[cls.__name__] = cls
    else:
        raise KeyError("{} was already defined as a JinjaEnum".format(cls.__name__))
    return cls
