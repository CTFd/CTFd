from CTFd.utils import get_config
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
    # TODO: Get values from config.py or config panel
    ctf_name = get_config('ctf_name')
    mailfrom_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
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