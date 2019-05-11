from flask import current_app as app, session, request
from CTFd.models import Users
from CTFd.utils import get_config
from CTFd.models import db, Fails
import datetime
import re


def get_current_user():
    if authed():
        user = Users.query.filter_by(id=session["id"]).first()
        return user
    else:
        return None


def get_current_team():
    if authed():
        user = get_current_user()
        return user.team
    else:
        return None


def authed():
    return bool(session.get("id", False))


def is_admin():
    if authed():
        return session["type"] == "admin"
    else:
        return False


def is_verified():
    if get_config("verify_emails"):
        user = get_current_user()
        if user:
            return user.verified
        else:
            return False
    else:
        return True


def get_ip(req=None):
    """ Returns the IP address of the currently in scope request. The approach is to define a list of trusted proxies
     (in this case the local network), and only trust the most recently defined untrusted IP address.
     Taken from http://stackoverflow.com/a/22936947/4285524 but the generator there makes no sense.
     The trusted_proxies regexes is taken from Ruby on Rails.

     This has issues if the clients are also on the local network so you can remove proxies from config.py.

     CTFd does not use IP address for anything besides cursory tracking of teams and it is ill-advised to do much
     more than that if you do not know what you're doing.
    """
    if req is None:
        req = request
    trusted_proxies = app.config["TRUSTED_PROXIES"]
    combined = "(" + ")|(".join(trusted_proxies) + ")"
    route = req.access_route + [req.remote_addr]
    for addr in reversed(route):
        if not re.match(combined, addr):  # IP is not trusted but we trust the proxies
            remote_addr = addr
            break
    else:
        remote_addr = req.remote_addr
    return remote_addr


def get_wrong_submissions_per_minute(account_id):
    """
    Get incorrect submissions per minute.

    :param account_id:
    :return:
    """
    one_min_ago = datetime.datetime.utcnow() + datetime.timedelta(minutes=-1)
    fails = (
        db.session.query(Fails)
        .filter(Fails.account_id == account_id, Fails.date >= one_min_ago)
        .all()
    )
    return len(fails)
