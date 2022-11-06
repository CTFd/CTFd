from CTFd.utils.email.providers.mailgun import MailgunEmailProvider


def sendmail(addr, text, subject):
    print(
        "CTFd.utils.email.mailgun.sendmail will raise an exception in a future minor release of CTFd and then be removed in CTFd v4.0"
    )
    return MailgunEmailProvider.sendmail(addr, text, subject)
