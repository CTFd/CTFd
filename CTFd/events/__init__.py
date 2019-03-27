from flask import current_app, Blueprint, Response, stream_with_context
from CTFd.utils.events import ServerSentEvent
import time

events = Blueprint('events', __name__)


@events.route("/events")
def subscribe():
    @stream_with_context
    def gen():
        sub = current_app.events_manager.subscribe()
        try:
            while True:
                message = sub.get()
                if message:
                    yield str(ServerSentEvent(**message))
                else:
                    yield str(ServerSentEvent(' '))
                time.sleep(1)
        except GeneratorExit:
            sub.unsubscribe()

    return Response(gen(), mimetype="text/event-stream")
