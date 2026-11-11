from flask import Blueprint, Response, current_app, stream_with_context

from CTFd.models import db
from CTFd.utils import get_app_config
from CTFd.utils.decorators import authed_only, ratelimit_from_config

events = Blueprint("events", __name__)


@events.route("/events")
@authed_only
@ratelimit_from_config(method="GET", config_key="RATELIMIT_EVENTS")
def subscribe():
    @stream_with_context
    def gen():
        for event in current_app.events_manager.subscribe():
            yield str(event)

    enabled = get_app_config("SERVER_SENT_EVENTS")
    if enabled is False:
        return ("", 204)

    # Close the db session to avoid OperationalError with MySQL connection errors
    db.session.close()

    return Response(gen(), mimetype="text/event-stream")
