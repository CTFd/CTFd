from CTFd.models import db, WrongKeys, Pages, Config
from CTFd import mail

from six.moves.urllib.parse import urlparse, urljoin 
from functools import wraps
from flask import current_app as app, g, request, redirect, url_for, session, render_template
from flask.ext.mail import Message
from socket import inet_aton, inet_ntoa
from struct import unpack, pack

import time
import datetime
import hashlib
import shutil
import requests
import logging
import os
import sys


def init_logs(app):
    logger_keys = logging.getLogger('keys')
    logger_logins = logging.getLogger('logins')
    logger_regs = logging.getLogger('regs')

    logger_keys.setLevel(logging.INFO)
    logger_logins.setLevel(logging.INFO)
    logger_regs.setLevel(logging.INFO)

    try:
        parent = os.path.dirname(__file__)
    except:
        parent = os.path.dirname(os.path.realpath(sys.argv[0]))

    log_dir = os.path.join(parent, 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logs = [
        os.path.join(parent, 'logs', 'keys.log'),
        os.path.join(parent, 'logs', 'logins.log'),
        os.path.join(parent, 'logs', 'registers.log')
    ]

    for log in logs:
        if not os.path.exists(log):
            open(log, 'a').close()

    key_log = logging.handlers.RotatingFileHandler(os.path.join(parent, 'logs', 'keys.log'), maxBytes=10000)
    login_log = logging.handlers.RotatingFileHandler(os.path.join(parent, 'logs', 'logins.log'), maxBytes=10000)
    register_log = logging.handlers.RotatingFileHandler(os.path.join(parent, 'logs', 'registers.log'), maxBytes=10000)

    logger_keys.addHandler(key_log)
    logger_logins.addHandler(login_log)
    logger_regs.addHandler(register_log)

    logger_keys.propagate = 0
    logger_logins.propagate = 0
    logger_regs.propagate = 0


def init_errors(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def general_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(502)
    def gateway_error(error):
        return render_template('errors/502.html'), 502

def init_utils(app):
    app.jinja_env.filters['unix_time'] = unix_time
    app.jinja_env.filters['unix_time_millis'] = unix_time_millis
    app.jinja_env.filters['long2ip'] = long2ip
    app.jinja_env.globals.update(pages=pages)
    app.jinja_env.globals.update(can_register=can_register)
    app.jinja_env.globals.update(mailserver=mailserver)
    app.jinja_env.globals.update(ctf_name=ctf_name)

    @app.context_processor
    def inject_user():
        if authed():
            return dict(session)
        return dict()

    @app.before_request
    def needs_setup():
        if request.path == '/setup' or request.path.startswith('/static'):
            return
        if not is_setup():
            return redirect('/setup')


def ctf_name():
    name = get_config('ctf_name')
    return name if name else 'CTFd'


def pages():
    pages = Pages.query.filter(Pages.route!="index").all()
    return pages


def authed():
    return bool(session.get('id', False))


def is_setup():
    setup = Config.query.filter_by(key='setup').first()
    if setup:
        return setup.value
    else:
        return False


def is_admin():
    if authed():
        return session['admin']
    else:
        return False


def can_register():
    config = Config.query.filter_by(key='prevent_registration').first()
    if config:
        return config.value != '1'
    else:
        return True


def admins_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin', None) is None:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


def view_after_ctf():
    if get_config('view_after_ctf') == '1' and time.time() > int(get_config("end")):
        return True
    else:
        return False

def ctftime():
    """ Checks whether it's CTF time or not. """

    start = get_config("start")
    end = get_config("end")

    if start:
        start = int(start)
    else:
        start = 0
    if end:
        end = int(end)
    else:
        end = 0

    if start and end:
        if start < time.time() < end:
            # Within the two time bounds
            return True

    if start < time.time() and end == 0: 
        # CTF starts on a date but never ends
        return True

    if start == 0 and time.time() < end: 
        # CTF started but ends at a date
        return True

    if start == 0 and end == 0:
        # CTF has no time requirements
        return True

    return False


def can_view_challenges():
    config = Config.query.filter_by(key="view_challenges_unregistered").first()
    if config:
        return authed() or config.value == '1'
    else:
        return authed()


def unix_time(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    delta = dt - epoch
    return int(delta.total_seconds())


def unix_time_millis(dt):
    return unix_time(dt) * 1000


def long2ip(ip_int):
    return inet_ntoa(pack('!I', ip_int))


def ip2long(ip):
    return unpack('!I', inet_aton(ip))[0]


def get_kpm(teamid): # keys per minute
    one_min_ago = datetime.datetime.utcnow() + datetime.timedelta(minutes=-1)
    return len(db.session.query(WrongKeys).filter(WrongKeys.team == teamid, WrongKeys.date >= one_min_ago).all())


def get_config(key):
    config = Config.query.filter_by(key=key).first()
    if config:
        return config.value
    else:
        return None


def set_config(key, value):
    config = Config.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Config(key, value)
        db.session.add(config)
    db.session.commit()
    return config


def mailserver():
    if (get_config('mg_api_key') and app.config['ADMINS']) or (app.config['MAIL_SERVER'] and app.config['MAIL_PORT'] and app.config['ADMINS']):
        return True
    return False


def sendmail(addr, text):
    if get_config('mg_api_key') and app.config['ADMINS']:
        ctf_name = get_config('ctf_name')
        mg_api_key = get_config('mg_api_key')
        return requests.post(
            "https://api.mailgun.net/v2/mail"+app.config['HOST']+"/messages",
            auth=("api", mg_api_key),
            data={"from": "{} Admin <{}>".format(ctf_name, app.config['ADMINS'][0]),
                  "to": [addr],
                  "subject": "Message from {0}".format(ctf_name),
                  "text": text})
    elif app.config['MAIL_SERVER'] and app.config['MAIL_PORT'] and app.config['ADMINS']:
        try:
            msg = Message("Message from {0}".format(get_config('ctf_name')), sender=app.config['ADMINS'][0], recipients=[addr])
            msg.body = text
            mail.send(msg)
            return True
        except:
            return False
    else:
        return False


def rmdir(dir):
    shutil.rmtree(dir, ignore_errors=True)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def validate_url(url):
    return urlparse(url).scheme.startswith('http')


def sha512(string):
    return hashlib.sha512(string).hexdigest()

