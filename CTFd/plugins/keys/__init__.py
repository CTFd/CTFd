import re
import string
import hmac


def ctfd_static_key_compare(saved, provided):
    return hmac.compare_digest(saved.lower(), provided.lower())

def ctfd_regex_key_compare(saved, provided):
    res = re.match(saved, provided, re.IGNORECASE)
    return res and res.group() == provided


KEY_FUNCTIONS = {
    0 : ctfd_static_key_compare,
    1 : ctfd_regex_key_compare
}


def get_key_function(func_id):
    func = KEY_FUNCTIONS.get(func_id)
    if func is None:
        raise KeyError
    return func
