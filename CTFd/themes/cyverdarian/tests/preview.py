"""Disposable local CTFd preview; never uses the configured production database."""

import datetime
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
os.chdir(REPO)
sys.path.insert(0, str(REPO))

from CTFd.config import TestingConfig
from CTFd.models import (
    ChallengeFiles, Challenges, Flags, Hints, Notifications, Pages,
    Solves, Teams, Users, db,
)
from CTFd.plugins.dynamic_challenges import DynamicChallenge
from CTFd.utils import set_config
from tests.helpers import create_ctfd


class PreviewConfig(TestingConfig):
    SERVER_NAME = "localhost:5080"
    UPLOAD_FOLDER = str(REPO / ".data/theme-preview-uploads")
    LOG_FOLDER = str(REPO / ".data/theme-preview-logs")
    SQLALCHEMY_DATABASE_URI = "sqlite://"


mode = "teams" if "--teams" in sys.argv else "users"
app = create_ctfd(
    user_mode=mode,
    config=PreviewConfig,
    ctf_name="Cyverdarian CTF",
    ctf_theme="cyverdarian",
    enable_plugins=True,
)

with app.app_context():
    for key, value in {
        "challenge_visibility": "public",
        "account_visibility": "public",
        "score_visibility": "public",
        "registration_visibility": "public",
        "challenge_ratings": "disabled",
        "view_self_submissions": True,
    }.items():
        set_config(key, value)

    Pages.query.filter_by(route="index").first().content = ""
    db.session.add(Pages(
        route="rules", title="Rules",
        content="<h1>Rules</h1><p>Play fair. Respect other participants.</p>",
    ))
    team = Teams(
        name="null_pointers", password="preview-password",
        affiliation="LVCC · BSIT 3A",
    )
    db.session.add(team)
    db.session.flush()
    player = Users(
        name="juan_dc", email="juan@example.test", password="preview-password",
        verified=True, team_id=team.id, affiliation="BSIT 3A",
    )
    db.session.add(player)
    db.session.flush()
    team.captain_id = player.id

    challenges = [
        ("Cookie Monster", "Web", 100),
        ("Caesar’s Lost Letter", "Crypto", 150),
        ("Base Camp", "Misc", 50),
        ("Hidden in Plain Sight", "Forensics", 100),
        ("Crackme 101", "Reverse", 250),
        ("Ghost in the Packet", "Forensics", 300),
        ("Union Station", "Web", 350),
        ("Stack of Bricks", "Pwn", 500),
    ]
    for index, (name, category, value) in enumerate(challenges):
        if index == 6:
            challenge = DynamicChallenge(
                name=name, category=category, initial=value, minimum=100,
                decay=20, type="dynamic", state="visible",
                description="A dynamic scoring challenge.",
            )
        else:
            challenge = Challenges(
                name=name, category=category, value=value, type="standard",
                state="visible", description=(
                    "The admin panel trusts whatever your browser hands it. "
                    "Find the cookie that opens the door and read the flag."
                ),
            )
        db.session.add(challenge)
        db.session.flush()
        db.session.add(Flags(
            challenge_id=challenge.id, type="static", content="flag{preview_success}",
        ))
        db.session.add(Hints(
            challenge_id=challenge.id, cost=0,
            content="Inspect the cookies in your browser.",
        ))
        if index in (1, 2, 3):
            db.session.add(Solves(
                user_id=player.id, team_id=team.id, challenge_id=challenge.id,
                ip="127.0.0.1", provided="flag{preview_success}",
                date=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
                - datetime.timedelta(hours=8 - index),
            ))

    db.session.add(Notifications(
        title="Welcome to the practice", content="Good luck and have fun!",
    ))
    attachment = Path(app.config["UPLOAD_FOLDER"]) / "preview/cookie_jar.txt"
    attachment.parent.mkdir(parents=True, exist_ok=True)
    attachment.write_text("Inspect your browser cookies. This is a test attachment.")
    db.session.add(ChallengeFiles(
        challenge_id=1, location="preview/cookie_jar.txt", type="challenge",
    ))
    db.session.commit()

    templates = REPO / "CTFd/themes/cyverdarian/templates"
    for template in templates.rglob("*.html"):
        app.jinja_env.get_template(template.relative_to(templates).as_posix())
    print("All theme templates compile.", flush=True)

app.run(host="127.0.0.1", port=5080, debug=False, use_reloader=False)
