from six.moves.urllib.parse import urlparse, urljoin, quote, unquote
from flask import request
import re


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def validate_url(url):
    return urlparse(url).scheme.startswith('http')


def validate_email(email):
    return bool(re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email))
