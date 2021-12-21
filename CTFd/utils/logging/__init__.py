import logging
import logging.handlers
from datetime import datetime

from flask import session

from CTFd.utils.user import get_ip


def log(logger, format, **kwargs):
    logger = logging.getLogger(logger)
    props = {
        "id": session.get("id"),
        "date": datetime.today().isoformat(),
        "ip": get_ip(),
    }
    props.update(kwargs)
    msg = format.format(**props)
    logger.info(msg, extra={'props': props})