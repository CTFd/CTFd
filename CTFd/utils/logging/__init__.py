import json
import logging
import logging.handlers
import time

from flask import has_request_context, session

from CTFd.utils.user import get_ip


def log(logger, format=None, **kwargs):
    props = {
        "logger": logger,
        "date": time.strftime("%m/%d/%Y %X"),
    }
    if has_request_context():
        props["id"] = session.get("id")
        props["ip"] = get_ip()
    props.update(kwargs)
    if format:
        msg = format.format(**props)
    else:
        msg = json.dumps(props)
    logger = logging.getLogger(logger)
    logger.info(msg)
