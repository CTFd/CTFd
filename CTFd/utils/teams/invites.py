from CTFd.utils.security.signing import unserialize
from CTFd.utils.encoding import base64decode
import json
import itsdangerous
from CTFd.models import Teams
from flask import current_app


def load_team_invite(code):
    # Inspect the invite object without loading it.
    # I am aware of loads_unsafe() but it seems safer to force json loading
    data = code.split(".")[0]
    unsafe_invite_obj = json.loads(base64decode(data))
    team_id = unsafe_invite_obj["id"]

    team = Teams.query.filter_by(id=team_id).first_or_404()

    secret = current_app.config["SECRET_KEY"] + team.password.encode("utf-8")

    # Verify that the data unserializes correctly
    try:
        unserialize(data=code, secret=secret, max_age=-1)
    except itsdangerous.exc.SignatureExpired:
        pass
    return team
