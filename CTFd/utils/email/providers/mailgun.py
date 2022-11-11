from email.utils import formataddr

import requests

from CTFd.utils import get_app_config, get_config
from CTFd.utils.email.providers import EmailProvider


class MailgunEmailProvider(EmailProvider):
    @staticmethod
    def sendmail(addr, text, subject):
        ctf_name = get_config("ctf_name")
        mailfrom_addr = get_config("mailfrom_addr") or get_app_config("MAILFROM_ADDR")
        mailfrom_addr = formataddr((ctf_name, mailfrom_addr))

        mailgun_base_url = get_config("mailgun_base_url") or get_app_config(
            "MAILGUN_BASE_URL"
        )
        mailgun_api_key = get_config("mailgun_api_key") or get_app_config(
            "MAILGUN_API_KEY"
        )
        try:
            r = requests.post(
                mailgun_base_url + "/messages",
                auth=("api", mailgun_api_key),
                data={
                    "from": mailfrom_addr,
                    "to": [addr],
                    "subject": subject,
                    "text": text,
                },
                timeout=1.0,
            )
        except requests.RequestException as e:
            return (
                False,
                "{error} exception occured while handling your request".format(
                    error=type(e).__name__
                ),
            )

        if r.status_code == 200:
            return True, "Email sent"
        else:
            return False, "Mailgun settings are incorrect"
