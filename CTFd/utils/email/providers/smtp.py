import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from socket import timeout

from CTFd.utils import get_app_config, get_config
from CTFd.utils.email.providers import EmailProvider


class SMTPEmailProvider(EmailProvider):
    @staticmethod
    def sendmail(addr, text, subject):
        ctf_name = get_config("ctf_name")
        mailfrom_addr = get_config("mailfrom_addr") or get_app_config("MAILFROM_ADDR")
        mailfrom_email = mailfrom_addr
        mailfrom_addr = formataddr((ctf_name, mailfrom_addr))

        custom_smtp = bool(get_config("mail_server"))
        if custom_smtp:
            host = get_config("mail_server")
            port = get_config("mail_port")
            username = get_config("mail_username")
            password = get_config("mail_password")
            TLS = get_config("mail_tls")
            SSL = get_config("mail_ssl")
            auth = get_config("mail_useauth")
        else:
            host = get_app_config("MAIL_SERVER")
            port = get_app_config("MAIL_PORT")
            username = get_app_config("MAIL_USERNAME")
            password = get_app_config("MAIL_PASSWORD")
            TLS = get_app_config("MAIL_TLS")
            SSL = get_app_config("MAIL_SSL")
            auth = get_app_config("MAIL_USEAUTH")

        data = {
            "host": host,
            "port": int(port),
        }

        if username:
            data["username"] = username
        if password:
            data["password"] = password
        if TLS:
            data["TLS"] = TLS
        if SSL:
            data["SSL"] = SSL
        if auth:
            data["auth"] = auth

        try:
            smtp = get_smtp(**data)

            msg = EmailMessage()
            msg.set_content(text)

            msg["Subject"] = subject
            msg["From"] = mailfrom_addr
            msg["To"] = addr
            msg["List-Unsubscribe"]= f"<mailto:{mailfrom_email}?subject=unsubscribe>"

            # We should only consider the MAILSENDER_ADDR value on servers defined in config
            if custom_smtp:
                smtp.send_message(msg)
            else:
                mailsender_addr = get_app_config("MAILSENDER_ADDR")
                smtp.send_message(msg, from_addr=mailsender_addr)

            smtp.quit()
            return True, "Email sent"
        except smtplib.SMTPException as e:
            return False, str(e)
        except timeout:
            return False, "SMTP server connection timed out"
        except Exception as e:
            return False, str(e)


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
