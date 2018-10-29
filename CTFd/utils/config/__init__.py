from flask import current_app as app
from CTFd.models import Configs, Users, Teams
from CTFd.cache import cache
from CTFd.utils import get_config
from CTFd.utils.user import authed
import time
import os


@cache.memoize()
def ctf_name():
    name = get_config('ctf_name')
    return name if name else 'CTFd'


@cache.memoize()
def user_mode():
    return get_config('user_mode')


@cache.memoize()
def ctf_logo():
    return get_config('ctf_logo')


@cache.memoize()
def ctf_theme():
    theme = get_config('ctf_theme')
    return theme if theme else ''


@cache.memoize()
def user_mode():
    return get_config('user_mode')


@cache.memoize()
def hide_scores():
    return get_config('hide_scores') or get_config('workshop_mode')


@cache.memoize()
def is_setup():
    setup = Configs.query.filter_by(key='setup').first()
    if setup:
        return setup.value
    else:
        return False


@cache.memoize()
def is_scoreboard_frozen():
    freeze = get_config('freeze')

    if freeze:
        freeze = int(freeze)
        if freeze < time.time():
            return True

    return False


@cache.memoize()
def can_send_mail():
    return mailserver() or mailgun()


@cache.memoize()
def mailgun():
    if app.config.get('MAILGUN_API_KEY') and app.config.get('MAILGUN_BASE_URL'):
        return True
    if get_config('mg_api_key') and get_config('mg_base_url'):
        return True
    return False


@cache.memoize()
def mailserver():
    if app.config.get('MAIL_SERVER') and app.config.get('MAIL_PORT'):
        return True
    if get_config('mail_server') and get_config('mail_port'):
        return True
    return False


@cache.memoize()
def get_themes():
    dir = os.path.join(app.root_path, 'themes')
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name)) and name != 'admin']
