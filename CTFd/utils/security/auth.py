import datetime
import os

from flask import session

from CTFd.cache import clear_user_session
from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.models import UserTokens, db
from CTFd.utils.encoding import hexencode
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import hmac


def login_user(user):
    session["id"] = user.id
    session["nonce"] = generate_nonce()
    session["hash"] = hmac(user.password)
    session.permanent = True

    # Clear out any currently cached user attributes
    clear_user_session(user_id=user.id)


def update_user(user):
    session["id"] = user.id
    session["hash"] = hmac(user.password)
    session.permanent = True

    # Clear out any currently cached user attributes
    clear_user_session(user_id=user.id)


def logout_user():
    session.clear()


def generate_user_token(user, expiration=None, description=None):
    temp_token = True
    while temp_token is not None:
        value = "ctfd_" + hexencode(os.urandom(32))
        temp_token = UserTokens.query.filter_by(value=value).first()

    token = UserTokens(
        user_id=user.id, expiration=expiration, description=description, value=value
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
