from flask import current_app as app
from CTFd.models import Config
from CTFd.utils import cache
from CTFd.utils import get_config
from CTFd.utils.user import authed
import time
import os


@cache.memoize()
def ctf_name():
    name = get_config('ctf_name')
    return name if name else 'CTFd'


@cache.memoize()
def ctf_logo():
    return get_config('ctf_logo')


@cache.memoize()
def ctf_theme():
    theme = get_config('ctf_theme')
    return theme if theme else ''


@cache.memoize()
def hide_scores():
    return get_config('hide_scores') or get_config('workshop_mode')


@cache.memoize()
def is_setup():
    setup = Config.query.filter_by(key='setup').first()
    if setup:
        return setup.value
    else:
        return False


@cache.memoize()
## TODO: Rename to registration_allowed
def can_register():
    return not bool(get_config('prevent_registration'))


@cache.memoize()
def view_after_ctf():
    return bool(get_config('view_after_ctf'))


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
    if get_config('mail_server') and get_config('mail_port'):
        return True
    return False


def user_can_view_challenges():
    config = bool(get_config('view_challenges_unregistered'))
    verify_emails = bool(get_config('verify_emails'))
    if config:
        return authed() or config
    else:
        return authed()


def get_themes():
    dir = os.path.join(app.root_path, 'themes')
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name)) and name != 'admin']