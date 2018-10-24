from flask import session
from CTFd.utils.user import get_ip
import logging
import logging.handlers
import os
import time


def init_logs(app):
    logger_submissions = logging.getLogger('submissions')
    logger_logins = logging.getLogger('logins')
    logger_registrations = logging.getLogger('registrations')

    logger_submissions.setLevel(logging.INFO)
    logger_logins.setLevel(logging.INFO)
    logger_registrations.setLevel(logging.INFO)

    log_dir = app.config['LOG_FOLDER']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logs = {
        'submissions': os.path.join(log_dir, 'submissions.log'),
        'logins': os.path.join(log_dir, 'logins.log'),
        'registrations': os.path.join(log_dir, 'registrations.log')
    }

    for log in logs.values():
        if not os.path.exists(log):
            open(log, 'a').close()

    submission_log = logging.handlers.RotatingFileHandler(logs['submissions'], maxBytes=10000)
    login_log = logging.handlers.RotatingFileHandler(logs['logins'], maxBytes=10000)
    registration_log = logging.handlers.RotatingFileHandler(logs['registrations'], maxBytes=10000)

    logger_submissions.addHandler(
        submission_log
    )
    logger_logins.addHandler(
        login_log
    )
    logger_registrations.addHandler(
        registration_log
    )

    logger_submissions.propagate = 0
    logger_logins.propagate = 0
    logger_registrations.propagate = 0


def log(logger, format, **kwargs):
    logger = logging.getLogger(logger)
    props = {
        'id': session.get('id'),
        'name': session.get('name'),
        'email': session.get('email'),
        'type': session.get('type'),
        'date': time.strftime("%m/%d/%Y %X"),
        'ip': get_ip()
    }
    props.update(kwargs)
    msg = format.format(**props)
    print(msg)
    logger.info(msg)
