from CTFd.utils.config import is_setup
from CTFd.utils import get_config, get_app_config


def mlc():
    if get_app_config("OAUTH_PROVIDER") != "mlc":
        return False
    if not is_setup():
        return True
    return get_config("oauth_client_id") and get_config("oauth_client_secret")


def ctftime():
    if get_app_config("OAUTH_PROVIDER") != "ctftime":
        return False
    if not is_setup():
        return True
    return get_config("oauth_client_id") and get_config("oauth_client_secret")


def oauth_registration():
    v = get_config("registration_visibility")
    return v in ["mlc", "ctftime"]
