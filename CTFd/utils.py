from CTFd.models import db, WrongKeys, Pages, Config, Tracking, Teams

from six.moves.urllib.parse import urlparse, urljoin 
from functools import wraps
from flask import current_app as app, g, request, redirect, url_for, session, render_template, abort
from itsdangerous import Signer, BadSignature
from socket import inet_aton, inet_ntoa
from struct import unpack, pack
from sqlalchemy.engine.url import make_url
from sqlalchemy import create_engine

import time
import datetime
import hashlib
import shutil
import requests
import logging
import os
import sys
import re
import time
import smtplib
import email

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
        if session:
            return dict(session)
        return dict()

    @app.before_request
    def needs_setup():
        if request.path == '/setup' or request.path.startswith('/static'):
            return
        if not is_setup():
            return redirect(url_for('views.setup'))

    @app.before_request
    def tracker():
        if authed():
            track = Tracking.query.filter_by(ip=ip2long(get_ip()), team=session['id']).first()
            if not track:
                visit = Tracking(ip=get_ip(), team=session['id'])
                db.session.add(visit)
                db.session.commit()
            else:
                track.date = datetime.datetime.utcnow()
                db.session.commit()
            db.session.close()

    @app.before_request
    def csrf():
        if not session.get('nonce'):
            session['nonce'] = sha512(os.urandom(10))
        if request.method == "POST":
            if session['nonce'] != request.form.get('nonce'):
                abort(403)


def ctf_name():
    name = get_config('ctf_name')
    return name if name else 'CTFd'


def pages():
    pages = Pages.query.filter(Pages.route!="index").all()
    return pages


def authed():
    return bool(session.get('id', False))

def is_verified():
    team = Teams.query.filter_by(id=session.get('id')).first()
    if team:
        return team.verified
    else:
        return False

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
            return redirect(url_for('auth.login'))
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
    return int((dt - datetime.datetime(1970, 1, 1)).total_seconds())


def unix_time_millis(dt):
    return unix_time(dt) * 1000


def get_ip():
    """ Returns the IP address of the currently in scope request. The approach is to define a list of trusted proxies
     (in this case the local network), and only trust the most recently defined untrusted IP address.
     Taken from http://stackoverflow.com/a/22936947/4285524 but the generator there makes no sense.
     The trusted_proxies regexes is taken from Ruby on Rails.

     This has issues if the clients are also on the local network so you can remove proxies from config.py.

     CTFd does not use IP address for anything besides cursory tracking of teams and it is ill-advised to do much
     more than that if you do not know what you're doing.
    """
    trusted_proxies = app.config['TRUSTED_PROXIES']
    combined = "(" + ")|(".join(trusted_proxies) + ")"
    route = request.access_route + [request.remote_addr]
    for addr in reversed(route):
        if not re.match(combined, addr): # IP is not trusted but we trust the proxies
            remote_addr = addr
            break
    else:
        remote_addr = request.remote_addr
    return remote_addr


def long2ip(ip_int):
    return inet_ntoa(pack('!I', ip_int))


def ip2long(ip):
    return unpack('!I', inet_aton(ip))[0]


def get_kpm(teamid): # keys per minute
    one_min_ago = datetime.datetime.utcnow() + datetime.timedelta(minutes=-1)
    return len(db.session.query(WrongKeys).filter(WrongKeys.teamid == teamid, WrongKeys.date >= one_min_ago).all())


def get_config(key):
    config = Config.query.filter_by(key=key).first()
    if config:
        value = config.value
        if value and value.isdigit():
            return int(value)
        else:
            return value
    else:
        set_config(key, None)
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
    if (get_config('mg_api_key')) or (get_config('mail_server') and get_config('mail_port')):
        return True
    return False


def get_smtp(host, port, username=None, password=None, TLS=None, SSL=None):
    smtp = smtplib.SMTP(host, port)
    smtp.ehlo()
    if TLS:
        smtp.starttls()
        smtp.ehlo()
    smtp.login(username, password)
    return smtp



def sendmail(addr, text):
    if get_config('mg_api_key') and get_config('mg_base_url'):
        ctf_name = get_config('ctf_name')
        mg_api_key = get_config('mg_api_key')
        mg_base_url = get_config('mg_base_url')
        r = requests.post(
            mg_base_url + '/messages',
            auth=("api", mg_api_key),
            data={"from": "{} Admin <{}>".format(ctf_name, 'noreply@ctfd.io'),
                  "to": [addr],
                  "subject": "Message from {0}".format(ctf_name),
                  "text": text})
        if r.status_code == 200:
            return True
        else:
            return False
    elif get_config('mail_server') and get_config('mail_port'):
        data = {
            'host': get_config('mail_server'),
            'port': int(get_config('mail_port'))
        }
        if get_config('mail_username'):
            data['username'] = get_config('mail_username')
        if get_config('mail_password'):
            data['password'] = get_config('mail_password')
        if get_config('mail_tls'):
            data['TLS'] = get_config('mail_tls')
        if get_config('mail_ssl'):
            data['SSL'] = get_config('mail_ssl')

        smtp = get_smtp(**data)
        msg = email.mime.text.MIMEText(text)
        msg['Subject'] = "Message from {0}".format(get_config('ctf_name'))
        msg['From'] = 'noreply@ctfd.io'
        msg['To'] = addr

        smtp.sendmail(msg['From'], [msg['To']], msg.as_string())
        smtp.quit()
        return True
    else:
        return False


def verify_email(addr):
    s = Signer(app.config['SECRET_KEY'])
    token = s.sign(addr)
    text = """Please click the following link to confirm your email address for {}: {}""".format(
        get_config('ctf_name'),
        url_for('auth.confirm_user', _external=True) + '/' + token.encode('base64')
    )
    sendmail(addr, text)


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

