from CTFd.utils import get_config


def mlc():
    return get_config("oauth_client_id") and get_config("oauth_client_secret")


def mlc_registration():
    v = get_config("registration_visibility")
    return v == "mlc"
