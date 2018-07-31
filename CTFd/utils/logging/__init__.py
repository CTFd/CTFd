import logging
import logging.handlers
import os


def init_logs(app):
    logger_keys = logging.getLogger('keys')
    logger_logins = logging.getLogger('logins')
    logger_regs = logging.getLogger('regs')

    logger_keys.setLevel(logging.INFO)
    logger_logins.setLevel(logging.INFO)
    logger_regs.setLevel(logging.INFO)

    log_dir = app.config['LOG_FOLDER']
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logs = {
        'keys': os.path.join(log_dir, 'keys.log'),
        'logins': os.path.join(log_dir, 'logins.log'),
        'registers': os.path.join(log_dir, 'registers.log')
    }

    for log in logs.values():
        if not os.path.exists(log):
            open(log, 'a').close()

    key_log = logging.handlers.RotatingFileHandler(logs['keys'], maxBytes=10000)
    login_log = logging.handlers.RotatingFileHandler(logs['logins'], maxBytes=10000)
    register_log = logging.handlers.RotatingFileHandler(logs['registers'], maxBytes=10000)

    logger_keys.addHandler(key_log)
    logger_logins.addHandler(login_log)
    logger_regs.addHandler(register_log)

    logger_keys.propagate = 0
    logger_logins.propagate = 0
    logger_regs.propagate = 0