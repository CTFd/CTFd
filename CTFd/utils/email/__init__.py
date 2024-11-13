from flask import url_for

from CTFd.utils import get_config
from CTFd.utils.config import get_mail_provider
from CTFd.utils.email.providers.mailgun import MailgunEmailProvider
from CTFd.utils.email.providers.smtp import SMTPEmailProvider
from CTFd.utils.formatters import safe_format
from CTFd.utils.security.signing import serialize

PROVIDERS = {"smtp": SMTPEmailProvider, "mailgun": MailgunEmailProvider}

DEFAULT_VERIFICATION_EMAIL_SUBJECT = "Confirm your account for {ctf_name}"
DEFAULT_VERIFICATION_EMAIL_BODY = (
    "Welcome to {ctf_name}!\n\n"
    "Click the following link to confirm and activate your account:\n"
    "{url}"
    "\n\n"
    "If the link is not clickable, try copying and pasting it into your browser."
)
DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT = "Successfully registered for {ctf_name}"
DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY = (
    "You've successfully registered for {ctf_name}!"
)
DEFAULT_USER_CREATION_EMAIL_SUBJECT = "Message from {ctf_name}"
DEFAULT_USER_CREATION_EMAIL_BODY = (
    "A new account has been created for you for {ctf_name} at {url}. \n\n"
    "Username: {name}\n"
    "Password: {password}"
)
DEFAULT_PASSWORD_RESET_SUBJECT = "Password Reset Request from {ctf_name}"
DEFAULT_PASSWORD_RESET_BODY = (
    "Did you initiate a password reset on {ctf_name}? "
    "If you didn't initiate this request you can ignore this email. \n\n"
    "Click the following link to reset your password:\n{url}\n\n"
    "If the link is not clickable, try copying and pasting it into your browser."
)
DEFAULT_PASSWORD_CHANGE_ALERT_SUBJECT = "Password Change Confirmation for {ctf_name}"
DEFAULT_PASSWORD_CHANGE_ALERT_BODY = (
    "Your password for {ctf_name} has been changed.\n\n"
    "If you didn't request a password change you can reset your password here:\n{url}\n\n"
    "If the link is not clickable, try copying and pasting it into your browser."
)


def sendmail(addr, text, subject="Message from {ctf_name}"):
    subject = safe_format(subject, ctf_name=get_config("ctf_name"))
    provider = get_mail_provider()
    EmailProvider = PROVIDERS.get(provider)
    if EmailProvider is None:
        return False, "No mail settings configured"
    return EmailProvider.sendmail(addr, text, subject)


def password_change_alert(email):
    text = safe_format(
        get_config("password_change_alert_body") or DEFAULT_PASSWORD_CHANGE_ALERT_BODY,
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        url=url_for("auth.reset_password", _external=True),
    )

    subject = safe_format(
        get_config("password_change_alert_subject")
        or DEFAULT_PASSWORD_CHANGE_ALERT_SUBJECT,
        ctf_name=get_config("ctf_name"),
    )
    return sendmail(addr=email, text=text, subject=subject)


def forgot_password(email):
    text = safe_format(
        get_config("password_reset_body") or DEFAULT_PASSWORD_RESET_BODY,
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        url=url_for("auth.reset_password", data=serialize(email), _external=True),
    )

    subject = safe_format(
        get_config("password_reset_subject") or DEFAULT_PASSWORD_RESET_SUBJECT,
        ctf_name=get_config("ctf_name"),
    )
    return sendmail(addr=email, text=text, subject=subject)


def verify_email_address(addr):
    text = safe_format(
        get_config("verification_email_body") or DEFAULT_VERIFICATION_EMAIL_BODY,
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        url=url_for(
            "auth.confirm", data=serialize(addr), _external=True, _method="GET"
        ),
    )

    subject = safe_format(
        get_config("verification_email_subject") or DEFAULT_VERIFICATION_EMAIL_SUBJECT,
        ctf_name=get_config("ctf_name"),
    )
    return sendmail(addr=addr, text=text, subject=subject)


def successful_registration_notification(addr):
    text = safe_format(
        get_config("successful_registration_email_body")
        or DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        url=url_for("views.static_html", _external=True),
    )

    subject = safe_format(
        get_config("successful_registration_email_subject")
        or DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
        ctf_name=get_config("ctf_name"),
    )
    return sendmail(addr=addr, text=text, subject=subject)


def user_created_notification(addr, name, password):
    text = safe_format(
        get_config("user_creation_email_body") or DEFAULT_USER_CREATION_EMAIL_BODY,
        ctf_name=get_config("ctf_name"),
        ctf_description=get_config("ctf_description"),
        url=url_for("views.static_html", _external=True),
        name=name,
        password=password,
    )

    subject = safe_format(
        get_config("user_creation_email_subject")
        or DEFAULT_USER_CREATION_EMAIL_SUBJECT,
        ctf_name=get_config("ctf_name"),
    )
    return sendmail(addr=addr, text=text, subject=subject)


def check_email_is_whitelisted(email_address):
    local_id, _, domain = email_address.partition("@")
    domain_whitelist = get_config("domain_whitelist")

    if domain_whitelist:
        domain_whitelist = [d.strip() for d in domain_whitelist.split(",")]

        for allowed_domain in domain_whitelist:
            if allowed_domain.startswith("*."):
                # domains should never container the "*" char
                if "*" in domain:
                    return False

                # Handle wildcard domain case
                suffix = allowed_domain[1:]  # Remove the "*" prefix
                if domain.endswith(suffix):
                    return True

            elif domain == allowed_domain:
                return True

        # whitelist is specified but the email doesn't match any domains
        return False

    # whitelist is not specified - allow all emails
    return True
