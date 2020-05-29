import hashlib
import hmac as _hmac

from flask import current_app
from itsdangerous import Signer
from itsdangerous.exc import (  # noqa: F401
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
)
from itsdangerous.url_safe import URLSafeTimedSerializer

from CTFd.utils import string_types


def serialize(data, secret=None):
    if secret is None:
        secret = current_app.config["SECRET_KEY"]
    s = URLSafeTimedSerializer(secret)
    return s.dumps(data)


def unserialize(data, secret=None, max_age=432000):
    if secret is None:
        secret = current_app.config["SECRET_KEY"]
    s = URLSafeTimedSerializer(secret)
    return s.loads(data, max_age=max_age)


def sign(data, secret=None):
    if secret is None:
        secret = current_app.config["SECRET_KEY"]
    s = Signer(secret)
    return s.sign(data)


def unsign(data, secret=None):
    if secret is None:
        secret = current_app.config["SECRET_KEY"]
    s = Signer(secret)
    return s.unsign(data)


def hmac(data, secret=None, digest=hashlib.sha1):
    if secret is None:
        secret = current_app.config["SECRET_KEY"]

    if isinstance(data, string_types):
        data = data.encode("utf-8")
    if isinstance(secret, string_types):
        secret = secret.encode("utf-8")

    return _hmac.new(key=secret, msg=data, digestmod=digest).hexdigest()
