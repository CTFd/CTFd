from CTFd.utils import get_app_config, get_config


def mlc():
    admin_config = get_config("oauth_client_id") and get_config("oauth_client_secret")
    main_config = get_app_config("OAUTH_CLIENT_ID") and get_app_config(
        "OAUTH_CLIENT_SECRET"
    )
    return admin_config or main_config

def name():
    return (
        get_app_config("OAUTH_NAME") or get_config("oauth_name") or "Major League Cyber"
    )

def mlc_registration():
    v = get_config("registration_visibility")
    return v == "mlc"
