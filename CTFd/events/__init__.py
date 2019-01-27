from flask import current_app, Blueprint, Response, stream_with_context

events = Blueprint('events', __name__)


@events.route("/events")
def subscribe():
    @stream_with_context
    def gen():
        for event in current_app.events_manager.subscribe():
            yield str(event)

    return Response(gen(), mimetype="text/event-stream")
