from flask import url_for
from CTFd.utils import get_config
from CTFd.utils.formatters import safe_format
from CTFd.utils.config import get_mail_provider
from CTFd.utils.email import mailgun, smtp
from CTFd.utils.security.signing import serialize


def sendmail(addr, text, subject="Message from {ctf_name}"):
    subject = safe_format(subject, ctf_name=get_config("ctf_name"))
    provider = get_mail_provider()
    if provider == "smtp":
        return smtp.sendmail(addr, text, subject)
    if provider == "mailgun":
        return mailgun.sendmail(addr, text, subject)
    return False, "No mail settings configured"


def password_change_alert(email):
    ctf_name = get_config("ctf_name")
    text = (
        "Your password for {ctf_name} has been changed.\n\n"
        "If you didn't request a password change you can reset your password here: {url}"
    ).format(ctf_name=ctf_name, url=url_for("auth.reset_password", _external=True))

    subject = "Password Change Confirmation for {ctf_name}".format(ctf_name=ctf_name)
    return sendmail(addr=email, text=text, subject=subject)


def forgot_password(email):
    token = serialize(email)
    text = """Did you initiate a password reset?  If you didn't initiate this request you can ignore this email.

Click the following link to reset your password:
{0}/{1}
""".format(
        url_for("auth.reset_password", _external=True), token
    )
    subject = "Password Reset Request from {ctf_name}"
    return sendmail(addr=email, text=text, subject=subject)


def verify_email_address(addr):
    token = serialize(addr)
    text = """Please click the following link to confirm your email address for {ctf_name}: {url}/{token}""".format(
        ctf_name=get_config("ctf_name"),
        url=url_for("auth.confirm", _external=True),
        token=token,
    )
    subject = "Confirm your account for {ctf_name}"
    return sendmail(addr=addr, text=text, subject=subject)


def user_created_notification(addr, name, password):
    text = """An account has been created for you for {ctf_name} at {url}. \n\nUsername: {name}\nPassword: {password}""".format(
        ctf_name=get_config("ctf_name"),
        url=url_for("views.static_html", _external=True),
        name=name,
        password=password,
    )
    return sendmail(addr, text)


def check_email_is_whitelisted(email_address):
    local_id, _, domain = email_address.partition("@")
    domain_whitelist = get_config("domain_whitelist")
    if domain_whitelist:
        domain_whitelist = [d.strip() for d in domain_whitelist.split(",")]
        if domain not in domain_whitelist:
            return False
    return True
