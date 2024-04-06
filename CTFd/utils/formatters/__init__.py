import re

from markupsafe import escape_silent


def safe_format(fmt, **kwargs):
    """
    Function that safely formats strings with arbitrary potentially user-supplied format strings
    Looks for interpolation placeholders like {target} or {{ target }}
    """
    # TODO: CTFd 4.0 - This function should probably be renamed to `safe_text_format`
    return re.sub(
        r"\{?\{([^{}]*)\}\}?", lambda m: kwargs.get(m.group(1).strip(), m.group(0)), fmt
    )


def safe_html_format(template, **kwargs):
    """
    Function that safely HTML escapes strings before safely formatting it into a HTML template
    """
    for k, v in kwargs.items():
        kwargs[k] = escape_silent(v)
    return safe_format(template, **kwargs)
