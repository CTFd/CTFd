from CTFd.utils import get_config, set_config


class UserMode(object):
    def __init__(self):
        pass

    def rules(self):
        pass


TEAM_SHARED = "user_team_login"
USER = "user_login"
TEAM_INDIVIDUAL = "team_login"


def get_user_mode():
    pass


def set_user_mode():
    pass


def allowed_in_current_user_mode(ctx):
    pass