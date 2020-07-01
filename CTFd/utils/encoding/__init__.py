import base64
import codecs

from CTFd.utils import string_types


def hexencode(s):
    if isinstance(s, string_types):
        s = s.encode("utf-8")
    encoded = codecs.encode(s, "hex")
    try:
        encoded = encoded.decode("utf-8")
    except UnicodeDecodeError:
        pass
    return encoded


def hexdecode(s):
    decoded = codecs.decode(s, "hex")
    try:
        decoded = decoded.decode("utf-8")
    except UnicodeDecodeError:
        pass
    return decoded


def base64encode(s):
    if isinstance(s, string_types):
        s = s.encode("utf-8")

    encoded = base64.urlsafe_b64encode(s).rstrip(b"\n=")
    try:
        encoded = encoded.decode("utf-8")
    except UnicodeDecodeError:
        pass
    return encoded


def base64decode(s):
    if isinstance(s, string_types):
        s = s.encode("utf-8")

    decoded = base64.urlsafe_b64decode(s.ljust(len(s) + len(s) % 4, b"="))
    try:
        decoded = decoded.decode("utf-8")
    except UnicodeDecodeError:
        pass
    return decoded
