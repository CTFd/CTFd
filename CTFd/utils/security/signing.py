from flask import current_app
from itsdangerous import Signer
from itsdangerous.exc import (  # noqa: F401
    BadSignature,
    BadTimeSignature,
    SignatureExpired,
)
from itsdangerous.url_safe import URLSafeTimedSerializer


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
