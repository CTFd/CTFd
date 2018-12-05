from CTFd.utils import get_config, get_app_config
from email.mime.text import MIMEText
from socket import timeout
import smtplib


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


def sendmail(addr, text):
    ctf_name = get_config('ctf_name')
    mailfrom_addr = get_config('mailfrom_addr') or get_app_config('MAILFROM_ADDR')
    data = {
        'host': get_config('mail_server'),
        'port': int(get_config('mail_port'))
    }
    username = get_config('mail_username') or get_app_config('MAIL_USERNAME')
    password = get_config('mail_password') or get_app_config('MAIL_PASSWORD')
    TLS = get_config('mail_tls') or get_app_config('MAIL_TLS')
    SSL = get_config('mail_ssl') or get_app_config('MAIL_SSL')
    auth = get_config('mail_useauth') or get_app_config('MAIL_USEAUTH')

    if username:
        data['username'] = username
    if password:
        data['password'] = password
    if TLS:
        data['TLS'] = TLS
    if SSL:
        data['SSL'] = SSL
    if auth:
        data['auth'] = auth

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
