from flask import Blueprint, Response, current_app, stream_with_context

from CTFd.utils import get_app_config, get_config
from CTFd.utils.decorators import authed_only, ratelimit
from CTFd.utils.modes import TEAMS_MODE
from CTFd.utils.user import get_current_team, get_current_user

events = Blueprint("events", __name__)


@events.route("/events")
@authed_only
@ratelimit(method="GET", limit=150, interval=60)
def subscribe():
    @stream_with_context
    def gen():
        for event in current_app.events_manager.subscribe():
            # Filter notifications based on user and team ID
            if event.type == "notification":
                if (
                    event.data["user"] is not None
                    and event.data["user"] != get_current_user().id
                ):
                    continue
                if get_config("user_mode") == TEAMS_MODE:
                    if (
                        event.data["team"] is not None
                        and event.data["team"] != get_current_team().id
                    ):
                        continue
            yield str(event)

    enabled = get_app_config("SERVER_SENT_EVENTS")
    if enabled is False:
        return ("", 204)

    return Response(gen(), mimetype="text/event-stream")
