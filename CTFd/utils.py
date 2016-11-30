from CTFd.models import db, WrongKeys, Pages, Config, Tracking, Teams, Containers, ip2long, long2ip

from six.moves.urllib.parse import urlparse, urljoin
import six
from werkzeug.utils import secure_filename
from functools import wraps
from flask import current_app as app, g, request, redirect, url_for, session, render_template, abort
from flask_caching import Cache
from itsdangerous import Signer, BadSignature
from socket import inet_aton, inet_ntoa, socket
from struct import unpack, pack, error
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
import tempfile
import subprocess
import urllib
import json

cache = Cache()


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
    app.jinja_env.globals.update(can_send_mail=can_send_mail)
    app.jinja_env.globals.update(ctf_name=ctf_name)
    app.jinja_env.globals.update(ctf_theme=ctf_theme)
    app.jinja_env.globals.update(can_create_container=can_create_container)

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


@cache.memoize()
def ctf_name():
    name = get_config('ctf_name')
    return name if name else 'CTFd'


@cache.memoize()
def ctf_theme():
    theme = get_config('ctf_theme')
    return theme if theme else ''


def pages():
    pages = Pages.query.filter(Pages.route!="index").all()
    return pages


def authed():
    return bool(session.get('id', False))


def is_verified():
    if get_config('verify_emails'):
        team = Teams.query.filter_by(id=session.get('id')).first()
        if team:
            return team.verified
        else:
            return False
    else:
        return True


@cache.memoize()
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


@cache.memoize()
def can_register():
    return not bool(get_config('prevent_registration'))


def admins_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin'):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('auth.login'))
    return decorated_function


@cache.memoize()
def view_after_ctf():
    return bool(get_config('view_after_ctf'))


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


def ctf_started():
    return time.time() > int(get_config("start") or 0)


def ctf_ended():
    if int(get_config("end") or 0):
        return time.time() > int(get_config("end") or 0)
    return False


def user_can_view_challenges():
    config = bool(get_config('view_challenges_unregistered'))
    verify_emails = bool(get_config('verify_emails'))
    if config:
        return authed() or config
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


def get_kpm(teamid): # keys per minute
    one_min_ago = datetime.datetime.utcnow() + datetime.timedelta(minutes=-1)
    return len(db.session.query(WrongKeys).filter(WrongKeys.teamid == teamid, WrongKeys.date >= one_min_ago).all())


def get_themes():
    dir = os.path.join(app.root_path, app.template_folder)
    return [name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name)) and name != 'admin']


@cache.memoize()
def get_config(key):
    config = Config.query.filter_by(key=key).first()
    if config and config.value:
        value = config.value
        if value and value.isdigit():
            return int(value)
        elif value and isinstance(value, six.string_types):
            if value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False
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


@cache.memoize()
def can_send_mail():
    return mailgun() or mailserver()


@cache.memoize()
def mailgun():
    if app.config.get('MAILGUN_API_KEY') and app.config.get('MAILGUN_BASE_URL'):
        return True
    if (get_config('mg_api_key') and get_config('mg_base_url')):
        return True
    return False


@cache.memoize()
def mailserver():
    if (get_config('mail_server') and get_config('mail_port')):
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
    ctf_name = get_config('ctf_name')
    mailfrom_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
    if mailgun():
        mg_api_key = get_config('mg_api_key') or app.config.get('MAILGUN_API_KEY')
        mg_base_url = get_config('mg_base_url') or app.config.get('MAILGUN_BASE_URL')
        
        r = requests.post(
            mg_base_url + '/messages',
            auth=("api", mg_api_key),
            data={"from": "{} Admin <{}>".format(ctf_name, mailfrom_addr),
                  "to": [addr],
                  "subject": "Message from {0}".format(ctf_name),
                  "text": text})
        if r.status_code == 200:
            return True
        else:
            return False
    elif mailserver():
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
        msg['Subject'] = "Message from {0}".format(ctf_name)
        msg['From'] = mailfrom_addr
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
        url_for('auth.confirm_user', _external=True) + '/' + urllib.quote_plus(token.encode('base64'))
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


@cache.memoize()
def can_create_container():
    try:
        output = subprocess.check_output(['docker', 'version'])
        return True
    except (subprocess.CalledProcessError, OSError):
        return False


def is_port_free(port):
    s = socket()
    result = s.connect_ex(('127.0.0.1', port))
    if result == 0:
        s.close()
        return False
    return True


def create_image(name, buildfile, files):
    if not can_create_container():
        return False
    folder = tempfile.mkdtemp(prefix='ctfd')
    tmpfile = tempfile.NamedTemporaryFile(dir=folder, delete=False)
    tmpfile.write(buildfile)
    tmpfile.close()

    for f in files:
        if f.filename.strip():
            filename = os.path.basename(f.filename)
            f.save(os.path.join(folder, filename))
    # repository name component must match "[a-z0-9](?:-*[a-z0-9])*(?:[._][a-z0-9](?:-*[a-z0-9])*)*"
    # docker build -f tmpfile.name -t name
    try:
        cmd = ['docker', 'build', '-f', tmpfile.name, '-t', name, folder]
        print cmd
        subprocess.call(cmd)
        container = Containers(name, buildfile)
        db.session.add(container)
        db.session.commit()
        db.session.close()
        rmdir(folder)
        return True
    except subprocess.CalledProcessError:
        return False


def delete_image(name):
    try:
        subprocess.call(['docker', 'rm', name])
        subprocess.call(['docker', 'rmi', name])
        return True
    except subprocess.CalledProcessError:
        return False


def run_image(name):
    try:
        info = json.loads(subprocess.check_output(['docker', 'inspect', '--type=image', name]))

        try:
            ports_asked = info[0]['Config']['ExposedPorts'].keys()
            ports_asked = [int(re.sub('[A-Za-z/]+', '', port)) for port in ports_asked]
        except KeyError:
            ports_asked = []

        cmd = ['docker', 'run', '-d']
        ports_used = []
        for port in ports_asked:
            if is_port_free(port):
                cmd.append('-p')
                cmd.append('{}:{}'.format(port, port))
            else:
                cmd.append('-p')
                ports_used.append('{}'.format(port))
        cmd += ['--name', name, name]
        print cmd
        subprocess.call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def container_start(name):
    try:
        cmd = ['docker', 'start', name]
        subprocess.call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def container_stop(name):
    try:
        cmd = ['docker', 'stop', name]
        subprocess.call(cmd)
        return True
    except subprocess.CalledProcessError:
        return False


def container_status(name):
    try:
        data = json.loads(subprocess.check_output(['docker', 'inspect', '--type=container', name]))
        status = data[0]["State"]["Status"]
        return status
    except subprocess.CalledProcessError:
        return 'missing'


def container_ports(name, verbose=False):
    try:
        info = json.loads(subprocess.check_output(['docker', 'inspect', '--type=container', name]))
        if verbose:
            ports = info[0]["NetworkSettings"]["Ports"]
            if not ports:
                return []
            final = []
            for port in ports.keys():
                final.append("".join([ports[port][0]["HostPort"], '->', port]))
            return final
        else:
            ports = info[0]['Config']['ExposedPorts'].keys()
            if not ports:
                return []
            ports = [int(re.sub('[A-Za-z/]+', '', port)) for port in ports_asked]
            return ports
    except subprocess.CalledProcessError:
        return []
