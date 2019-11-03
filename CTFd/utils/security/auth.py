from CTFd.models import db, Users, UserTokens
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import serialize, unserialize
from CTFd.utils.dates import unix_time, unix_time_to_utc
from CTFd.utils.encoding import hexencode
from CTFd.exceptions import UserNotFoundException, APIKeyExpiredException
from flask import session
import datetime
import os


def login_user(user):
    session["id"] = user.id
    session["name"] = user.name
    session["type"] = user.type
    session["email"] = user.email
    session["nonce"] = generate_nonce()


def logout_user():
    session.clear()


def generate_api_key(user, expiration=None):
    temp_token = True
    while temp_token is not None:
        value = hexencode(os.urandom(32))
        temp_token = UserTokens.query.filter_by(value=value).first()

    token = UserTokens(
        user_id=user.id,
        expiration=expiration,
        value=hexencode(os.urandom(32))
    )
    db.session.add(token)
    db.session.commit()
    return token


def lookup_api_key(key):
    token = UserTokens.query.filter_by(value=key).first()
    if token:
        return token.user
    return None