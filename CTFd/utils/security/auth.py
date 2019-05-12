from CTFd.utils.security.csrf import generate_nonce
from flask import session


def login_user(user):
    session["id"] = user.id
    session["name"] = user.name
    session["type"] = user.type
    session["email"] = user.email
    session["nonce"] = generate_nonce()


def logout_user():
    session.clear()
