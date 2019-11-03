from CTFd.models import Users
from CTFd.utils.security.csrf import generate_nonce
from CTFd.utils.security.signing import serialize, unserialize
from CTFd.utils.dates import unix_time, unix_time_to_utc
from CTFd.exceptions import UserNotFoundException, APIKeyExpiredException
from flask import session
import datetime


def login_user(user):
    session["id"] = user.id
    session["name"] = user.name
    session["type"] = user.type
    session["email"] = user.email
    session["nonce"] = generate_nonce()


def logout_user():
    session.clear()


def generate_api_key(user, valid_until=None):
    valid_until = unix_time(valid_until) if valid_until else 0
    return serialize(
        {"id": user.id, "data": serialize({"v": valid_until}, secret=user.secret)}
    )


def lookup_api_key(key):
    # Unserialize but max_age is user specified in the data section
    key = unserialize(key, max_age=None)
    user_id = key["id"]
    user_data = key["data"]
    valid_until = unix_time_to_utc(user_data["v"])

    user = Users.query.filter_by(id=user_id).first()
    if user is None:
        raise UserNotFoundException
    if datetime.datetime.utcnow() <= valid_until:
        raise APIKeyExpiredException

    return user
