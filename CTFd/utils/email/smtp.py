from CTFd.utils.email.providers.smtp import SMTPEmailProvider


def sendmail(addr, text, subject):
    print(
        "CTFd.utils.email.smtp.sendmail will raise an exception in a future minor release of CTFd and then be removed in CTFd v4.0"
    )
    return SMTPEmailProvider.sendmail(addr, text, subject)
