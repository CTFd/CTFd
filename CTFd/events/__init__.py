from flask import current_app, Blueprint, Response, stream_with_context
from CTFd.utils.decorators import authed_only, ratelimit

events = Blueprint("events", __name__)


@events.route("/events")
@authed_only
@ratelimit(method="GET", limit=150, interval=60)
def subscribe():
    @stream_with_context
    def gen():
        for event in current_app.events_manager.subscribe():
            yield str(event)

    return Response(gen(), mimetype="text/event-stream")
