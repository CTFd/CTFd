from flask import session
from CTFd.utils.user import get_ip
import logging
import logging.handlers
import time


def log(logger, format, **kwargs):
    logger = logging.getLogger(logger)
    props = {
        "id": session.get("id"),
        "name": session.get("name"),
        "email": session.get("email"),
        "type": session.get("type"),
        "date": time.strftime("%m/%d/%Y %X"),
        "ip": get_ip(),
    }
    props.update(kwargs)
    msg = format.format(**props)
    print(msg)
    logger.info(msg)
