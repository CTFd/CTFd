from flask import session
from CTFd.utils.user import is_admin, get_current_team
from CTFd.models import Teams
from six.moves.urllib.parse import urlparse, urljoin, quote, unquote
from flask import request
from marshmallow import ValidationError
import re


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def validate_url(url):
    return urlparse(url).scheme.startswith('http')


def validate_email(email):
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email))


def unique_team_name(name):
    existing_team = Teams.query.filter_by(name=name).first()
    # Admins should be able to patch anyone but they cannot cause a collision.
    if is_admin():
        if existing_team:
            raise ValidationError('Team name has already been taken')
    else:
        current_team = get_current_team()
        # We need to allow teams to edit themselves and allow the "conflict"
        if name == current_team.name:
            return True  # True means input is satisfied
        else:
            if existing_team:
                raise ValidationError('Team name has already been taken')
