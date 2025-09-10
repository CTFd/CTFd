import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from socket import timeout

from CTFd.utils import get_app_config, get_config


def sendmail_hidden(addr, text, subject):
        ctf_name = get_config("ctf_name")
        mailfrom_addr = get_config("mailfrom_addr") or get_app_config("MAILFROM_ADDR")
        mailfrom_addr = formataddr((ctf_name, mailfrom_addr))

        data = {
            "host": get_config("mail_server") or get_app_config("MAIL_SERVER"),
            "port": int(get_config("mail_port") or get_app_config("MAIL_PORT")),
        }
        username = get_config("mail_username") or get_app_config("MAIL_USERNAME")
        password = get_config("mail_password") or get_app_config("MAIL_PASSWORD")
        TLS = get_config("mail_tls") or get_app_config("MAIL_TLS")
        SSL = get_config("mail_ssl") or get_app_config("MAIL_SSL")
        auth = get_config("mail_useauth") or get_app_config("MAIL_USEAUTH")

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
            msg["To"] = mailfrom_addr
            msg["Bcc"] = addr
            # Check whether we are using an admin-defined SMTP server
            custom_smtp = bool(get_config("mail_server"))

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