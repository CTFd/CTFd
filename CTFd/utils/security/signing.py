from flask import current_app
from itsdangerous.url_safe import URLSafeSerializer, URLSafeTimedSerializer
from itsdangerous.exc import BadTimeSignature, SignatureExpired, BadSignature


def serialize(data):
    secret = current_app.config['SECRET_KEY']
    s = URLSafeTimedSerializer(secret)
    return s.dumps(data)


def unserialize(data, max_age=432000):
    secret = current_app.config['SECRET_KEY']
    s = URLSafeTimedSerializer(secret)
    return s.loads(data, max_age=max_age)
