from flask import current_app as app, url_for
from CTFd.utils import cache, get_config, get_app_config
from CTFd.utils.config import mailgun, can_send_mail, mailserver
from CTFd.utils.encoding import base64decode, base64encode
from email.mime.text import MIMEText
from itsdangerous import TimedSerializer, BadTimeSignature, Signer, BadSignature
from socket import timeout
import smtplib
import requests


def sendmail(addr, text):
    ctf_name = get_config('ctf_name')
    mailfrom_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
    if mailgun():
        if get_config('mg_api_key') and get_config('mg_base_url'):
            mg_api_key = get_config('mg_api_key')
            mg_base_url = get_config('mg_base_url')
        elif app.config.get('MAILGUN_API_KEY') and app.config.get('MAILGUN_BASE_URL'):
            mg_api_key = app.config.get('MAILGUN_API_KEY')
            mg_base_url = app.config.get('MAILGUN_BASE_URL')
        else:
            return False, "Mailgun settings are missing"

        try:
            r = requests.post(
                mg_base_url + '/messages',
                auth=("api", mg_api_key),
                data={"from": "{} Admin <{}>".format(ctf_name, mailfrom_addr),
                      "to": [addr],
                      "subject": "Message from {0}".format(ctf_name),
                      "text": text},
                timeout=1.0
            )
        except requests.RequestException as e:
            return False, "{error} exception occured while handling your request".format(error=type(e).__name__)

        if r.status_code == 200:
            return True, "Email sent"
        else:
            return False, "Mailgun settings are incorrect"
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
        if get_config('mail_useauth'):
            data['auth'] = get_config('mail_useauth')

        try:
            smtp = get_smtp(**data)
            msg = MIMEText(text)
            msg['Subject'] = "Message from {0}".format(ctf_name)
            msg['From'] = mailfrom_addr
            msg['To'] = addr

            smtp.sendmail(msg['From'], [msg['To']], msg.as_string())
            smtp.quit()
            return True, "Email sent"
        except smtplib.SMTPException as e:
            return False, str(e)
        except timeout:
            return False, "SMTP server connection timed out"
        except Exception as e:
            return False, str(e)
    else:
        return False, "No mail settings configured"


def forgot_password(email, team_name):
    s = TimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps(team_name)
    text = """Did you initiate a password reset? Click the following link to reset your password:

{0}/{1}

""".format(url_for('auth.reset_password', _external=True), base64encode(token))

    sendmail(email, text)


def verify_email_address(addr):
    s = TimedSerializer(app.config['SECRET_KEY'])
    token = s.dumps(addr)
    text = """Please click the following link to confirm your email address for {ctf_name}: {url}/{token}""".format(
        ctf_name=get_config('ctf_name'),
        url=url_for('auth.confirm', _external=True),
        token=base64encode(token)
    )
    sendmail(addr, text)


def get_smtp(host, port, username=None, password=None, TLS=None, SSL=None, auth=None):
    if SSL is None:
        smtp = smtplib.SMTP(host, port, timeout=3)
    else:
        smtp = smtplib.SMTP_SSL(host, port, timeout=3)

    if TLS:
        smtp.starttls()

    if auth:
        smtp.login(username, password)
    return smtp


