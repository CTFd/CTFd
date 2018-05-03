import base64
import six

def urlsafe_base64_encode(s):
    """
    Encode a bytestring in base64 for use in URLs. Strip any trailing equal
    signs.
    """
    return base64.urlsafe_b64encode(s).rstrip(b'\n=')


def urlsafe_base64_decode(s):
    """
    Decode a base64 encoded string. Add back any trailing equal signs that
    might have been stripped.
    """
    if six.PY3 and isinstance(s, six.string_types):
        s = s.encode('utf-8')
    else:
        # Python 2 support because the base64 module doesnt like unicode
        s = str(s)
    try:
        return base64.urlsafe_b64decode(s.ljust(len(s) + len(s) % 4, b'='))
    except (LookupError, base64.binascii.Error) as e:
        raise ValueError(e)
