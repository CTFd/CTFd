import re
from urllib.parse import urljoin, urlparse

from flask import request
from marshmallow import ValidationError

from CTFd.models import Users
from CTFd.utils.countries import lookup_country_code
from CTFd.utils.user import get_current_user, is_admin

EMAIL_REGEX = r"(^[^@\s]+@[^@\s]+\.[^@\s]+$)"


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def validate_url(url):
    return urlparse(url).scheme.startswith("http")


def validate_email(email):
    return bool(re.match(EMAIL_REGEX, email))


def unique_email(email, model=Users):
    obj = model.query.filter_by(email=email).first()
    if is_admin():
        if obj:
            raise ValidationError("Email address has already been used")
    if obj and obj.id != get_current_user().id:
        raise ValidationError("Email address has already been used")


def validate_country_code(country_code):
    if country_code.strip() == "":
        return
    if lookup_country_code(country_code) is None:
        raise ValidationError("Invalid Country")
