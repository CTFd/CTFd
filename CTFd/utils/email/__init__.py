from flask import url_for
from CTFd.utils import get_config
from CTFd.utils.config import get_mail_provider
from CTFd.utils.email import mailgun, smtp
from CTFd.utils.security.signing import serialize
import re


EMAIL_REGEX = r"(^[^@\s]+@[^@\s]+\.[^@\s]+$)"


def sendmail(addr, text):
    provider = get_mail_provider()
    if provider == "smtp":
        return smtp.sendmail(addr, text)
    if provider == "mailgun":
        return mailgun.sendmail(addr, text)
    return False, "No mail settings configured"


def forgot_password(email, team_name):
    token = serialize(team_name)
    text = """Did you initiate a password reset? Click the following link to reset your password:

{0}/{1}

""".format(
        url_for("auth.reset_password", _external=True), token
    )

    return sendmail(email, text)


def verify_email_address(addr):
    token = serialize(addr)
    text = """Please click the following link to confirm your email address for {ctf_name}: {url}/{token}""".format(
        ctf_name=get_config("ctf_name"),
        url=url_for("auth.confirm", _external=True),
        token=token,
    )
    return sendmail(addr, text)


def user_created_notification(addr, name, password):
    text = """An account has been created for you for {ctf_name} at {url}. \n\nUsername: {name}\nPassword: {password}""".format(
        ctf_name=get_config("ctf_name"),
        url=url_for("views.static_html", _external=True),
        name=name,
        password=password,
    )
    return sendmail(addr, text)


def check_email_format(email):
    return bool(re.match(EMAIL_REGEX, email))


def check_email_is_whitelisted(email_address):
    local_id, _, domain = email_address.partition("@")
    domain_whitelist = get_config("domain_whitelist")
    if domain_whitelist:
        domain_whitelist = [d.strip() for d in domain_whitelist.split(",")]
        if domain not in domain_whitelist:
            return False
    return True
