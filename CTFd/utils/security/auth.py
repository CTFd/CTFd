import datetime
import os

from flask import session

from CTFd.cache import clear_user_session
from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.models import Users, UserTokens, db
from CTFd.utils import get_app_config
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


def generate_preset_admin():
    from CTFd.utils.logging import log

    # Check if user already exists
    preset_admin_name = get_app_config("PRESET_ADMIN_NAME")
    preset_admin_email = get_app_config("PRESET_ADMIN_EMAIL")
    preset_admin_password = get_app_config("PRESET_ADMIN_PASSWORD")

    # We should only promote by email as name may not correctly associate
    user = Users.query.filter_by(email=preset_admin_email).first()

    if user is None:
        # Create the preset admin user
        user = Users(
            name=preset_admin_name,
            email=preset_admin_email,
            password=preset_admin_password,
            type="admin",
            verified=True,
        )
        db.session.add(user)
        db.session.commit()
        log(
            "registrations",
            "[{date}] {ip} - preset admin {name} created",
            name=user.name,
        )

    # If there's already a user, promoting it to an admin represents a mild security risk.
    if user.type != "admin":
        return None

    return user


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
    preset_admin_token = get_app_config("PRESET_ADMIN_TOKEN")
    if preset_admin_token and token == preset_admin_token:
        preset_admin = generate_preset_admin()
        if preset_admin:
            return preset_admin
    token = UserTokens.query.filter_by(value=token).first()
    if token:
        if datetime.datetime.utcnow() >= token.expiration:
            raise UserTokenExpiredException
        return token.user
    else:
        raise UserNotFoundException
