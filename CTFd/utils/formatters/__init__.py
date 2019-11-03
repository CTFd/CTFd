import re


def safe_format(fmt, **kwargs):
    """
    Function that safely formats strings with arbitrary potentially user-supplied format strings
    Looks for interpolation placeholders like {target} or {{ target }}
    """
    return re.sub(
        r"\{?\{([^{}]*)\}\}?", lambda m: kwargs.get(m.group(1).strip(), m.group(0)), fmt
    )
