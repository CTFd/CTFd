from flask import current_app as app
from CTFd.utils import get_config

def mlc():
    return get_config('oauth_client_id') and get_config('oauth_client_secret')
