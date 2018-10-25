from flask import current_app as app, url_for
from CTFd.utils import get_config, get_app_config
from CTFd.utils.config import mailgun, can_send_mail, mailserver
from CTFd.utils.encoding import base64decode, base64encode
from CTFd.utils.email import mailgun, smtp
from itsdangerous import TimedSerializer, BadTimeSignature, Signer, BadSignature


def sendmail(addr, text):
    if mailserver():
        return smtp.sendmail(addr, text)

    if mailgun():
        return mailgun.sendmail(addr, text)

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


