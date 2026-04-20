import re
import unicodedata
from urllib.parse import urljoin, urlparse, urlsplit

from flask import request
from marshmallow import ValidationError

from CTFd.constants.languages import LANGUAGE_NAMES
from CTFd.models import Users
from CTFd.utils.countries import lookup_country_code
from CTFd.utils.user import get_current_user, is_admin

EMAIL_REGEX = r"(^[^@\s]+@[^@\s]+\.[^@\s]+$)"
MAX_URL_LENGTH = 2048


def is_safe_url(target):
    """
    is_safe_url and _is_safe_url is mostly ported from Pallets snippets and Django's url_has_allowed_host_and_scheme
    """
    # Chrome treats \ completely as / in paths but it could be part of some
    # basic auth credentials so we need to check both URLs.
    return _is_safe_url(target) and _is_safe_url(target.replace("\\", "/"))


def _is_safe_url(target):
    # TODO: CTFd 4.0 In Django this was renamed to `url_has_allowed_host_and_scheme`. Consider similar.
    if target.startswith("///") or len(target) > MAX_URL_LENGTH:
        # urlsplit does not perform validation of inputs. Unicode normalization
        # is very slow on Windows and can be a DoS attack vector.
        # https://docs.python.org/3/library/urllib.parse.html#url-parsing-security
        return False
    try:
        url_info = urlsplit(target)
    except ValueError:  # e.g. invalid IPv6 addresses
        return False
    # Forbid URLs like http:///example.com - with a scheme, but without a
    # hostname. In that URL, example.com is not the hostname but, a path
    # component. However, Chrome will still consider example.com to be the
    # hostname, so we must not allow this syntax.
    if not url_info.netloc and url_info.scheme:
        return False
    # Forbid URLs that start with control characters. Some browsers (like
    # Chrome) ignore quite a few control characters at the start of a
    # URL and might consider the URL as scheme relative.
    if unicodedata.category(target[0])[0] == "C":
        return False
    # The below came from Pallets snippets however it is insufficient
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


def validate_url(url):
    return urlparse(url).scheme.startswith("http")


def validate_email(email):
    # https://github.com/django/django/blob/bc9b6251e0b54c3b5520e3c66578041cc17e4a28/django/core/validators.py#L257
    if not email or "@" not in email or len(email) > 320:
        return False
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


def validate_language(language):
    if language.strip() == "":
        return
    if LANGUAGE_NAMES.get(language) is None:
        raise ValidationError("Invalid Language")
