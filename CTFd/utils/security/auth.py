import datetime
import os

from flask import session

from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.models import UserTokens, db
from CTFd.utils.encoding import hexencode
from CTFd.utils.security.csrf import generate_nonce


def login_user(user):
    session["id"] = user.id
    session["name"] = user.name
    session["type"] = user.type
    session["email"] = user.email
    session["nonce"] = generate_nonce()


def logout_user():
    session.clear()


def generate_user_token(user, expiration=None):
    temp_token = True
    while temp_token is not None:
        value = hexencode(os.urandom(32))
        temp_token = UserTokens.query.filter_by(value=value).first()

    token = UserTokens(
        user_id=user.id, expiration=expiration, value=hexencode(os.urandom(32))
    )
    db.session.add(token)
    db.session.commit()
    return token


def lookup_user_token(token):
    token = UserTokens.query.filter_by(value=token).first()
    if token:
        if datetime.datetime.utcnow() >= token.expiration:
            raise UserTokenExpiredException
        return token.user
    else:
        raise UserNotFoundException
    return None
