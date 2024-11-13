import datetime
import gc
import random
import string
import uuid
from collections import namedtuple
from contextlib import contextmanager
from unittest.mock import Mock, patch

import requests
from flask.testing import FlaskClient
from freezegun import freeze_time
from sqlalchemy.engine.url import make_url
from sqlalchemy_utils import drop_database
from werkzeug.datastructures import Headers

from CTFd import create_app
from CTFd.cache import cache, clear_challenges, clear_standings
from CTFd.config import TestingConfig
from CTFd.constants.themes import DEFAULT_THEME
from CTFd.models import (
    Awards,
    Brackets,
    ChallengeComments,
    ChallengeFiles,
    Challenges,
    ChallengeTopics,
    Comments,
    Fails,
    Fields,
    Files,
    Flags,
    Hints,
    Notifications,
    PageComments,
    PageFiles,
    Pages,
    Solves,
    Tags,
    TeamComments,
    Teams,
    Tokens,
    Topics,
    Tracking,
    Unlocks,
    UserComments,
    Users,
)
from CTFd.utils import set_config
from tests.constants.time import FreezeTimes

text_type = str
binary_type = bytes


FakeRequest = namedtuple("FakeRequest", ["form"])


class CTFdTestClient(FlaskClient):
    def open(self, *args, **kwargs):
        if kwargs.get("json") is not None:
            with self.session_transaction() as sess:
                api_key_headers = Headers({"CSRF-Token": sess.get("nonce")})
                headers = kwargs.pop("headers", Headers())
                if isinstance(headers, dict):
                    headers = Headers(headers)
                headers.extend(api_key_headers)
                kwargs["headers"] = headers
        return super(CTFdTestClient, self).open(*args, **kwargs)


class ctftime:
    @contextmanager
    def init():
        """
        This context manager can be used to setup start and end dates for a test CTFd
        """
        try:
            set_config("start", FreezeTimes.START)
            set_config("end", FreezeTimes.END)
            yield
        finally:
            set_config("start", None)
            set_config("end", None)

    @contextmanager
    def not_started():
        """
        This context manager sets the current time to before the start date of the test CTFd
        """
        try:
            freezer = freeze_time(FreezeTimes.NOT_STARTED)
            frozen_time = freezer.start()
            yield frozen_time
        finally:
            freezer.stop()

    @contextmanager
    def started():
        """
        This context manager sets the current time to the start date of the test CTFd
        """
        try:
            freezer = freeze_time(FreezeTimes.STARTED)
            frozen_time = freezer.start()
            yield frozen_time
        finally:
            freezer.stop()

    @contextmanager
    def ended():
        """
        This context manager sets the current time to after the end date of the test CTFd
        """
        try:
            freezer = freeze_time(FreezeTimes.ENDED)
            frozen_time = freezer.start()
            yield frozen_time
        finally:
            freezer.stop()


def create_ctfd(
    ctf_name="CTFd",
    ctf_description="CTF description",
    name="admin",
    email="admin@examplectf.com",
    password="password",
    user_mode="users",
    setup=True,
    enable_plugins=False,
    application_root="/",
    config=TestingConfig,
    ctf_theme=None,
):
    if enable_plugins:
        config.SAFE_MODE = False
    else:
        config.SAFE_MODE = True

    if ctf_theme is None:
        ctf_theme = DEFAULT_THEME

    config.APPLICATION_ROOT = application_root
    url = make_url(config.SQLALCHEMY_DATABASE_URI)
    if url.database:
        url = url.set(database=str(uuid.uuid4()))
    config.SQLALCHEMY_DATABASE_URI = str(url)

    app = create_app(config)
    app.test_client_class = CTFdTestClient

    if setup:
        app = setup_ctfd(
            app,
            ctf_name=ctf_name,
            ctf_description=ctf_description,
            name=name,
            email=email,
            password=password,
            user_mode=user_mode,
            ctf_theme=ctf_theme,
        )
    return app


def setup_ctfd(
    app,
    ctf_name="CTFd",
    ctf_description="CTF description",
    name="admin",
    email="admin@examplectf.com",
    password="password",
    user_mode="users",
    ctf_theme=None,
):
    if ctf_theme is None:
        ctf_theme = DEFAULT_THEME
    with app.app_context():
        with app.test_client() as client:
            client.get("/setup")  # Populate session with nonce
            with client.session_transaction() as sess:
                data = {
                    "ctf_name": ctf_name,
                    "ctf_description": ctf_description,
                    "name": name,
                    "email": email,
                    "password": password,
                    "user_mode": user_mode,
                    "nonce": sess.get("nonce"),
                    "ctf_theme": ctf_theme,
                }
            client.post("/setup", data=data)
    return app


def destroy_ctfd(app):
    with app.app_context():
        gc.collect()  # Garbage collect (necessary in the case of dataset freezes to clean database connections)
        cache.clear()
        drop_database(app.config["SQLALCHEMY_DATABASE_URI"])


def register_user(
    app,
    name="user",
    email="user@examplectf.com",
    password="password",
    bracket_id=None,
    raise_for_error=True,
):
    with app.app_context():
        with app.test_client() as client:
            client.get("/register")
            with client.session_transaction() as sess:
                data = {
                    "name": name,
                    "email": email,
                    "password": password,
                    "nonce": sess.get("nonce"),
                }
            if bracket_id:
                data["bracket_id"] = bracket_id
            client.post("/register", data=data)
            if raise_for_error:
                with client.session_transaction() as sess:
                    assert sess["id"]
                    assert sess["nonce"]
                    assert sess["hash"]


def register_team(app, name="team", password="password", raise_for_error=True):
    with app.app_context():
        with app.test_client() as client:
            client.get("/team")
            with client.session_transaction() as sess:
                data = {"name": name, "password": password, "nonce": sess.get("nonce")}
            r = client.post("/teams/new", data=data)
            if raise_for_error:
                assert r.status_code == 302
            return client


def login_as_user(app, name="user", password="password", raise_for_error=True):
    with app.app_context():
        with app.test_client() as client:
            client.get("/login")
            with client.session_transaction() as sess:
                data = {"name": name, "password": password, "nonce": sess.get("nonce")}
            client.post("/login", data=data)
            if raise_for_error:
                with client.session_transaction() as sess:
                    assert sess["id"]
                    assert sess["nonce"]
                    assert sess["hash"]
            return client


def login_with_mlc(
    app,
    name="user",
    scope="profile%20team",
    email="user@examplectf.com",
    oauth_id=1337,
    team_name="TestTeam",
    team_oauth_id=1234,
    raise_for_error=True,
):
    with app.test_client() as client, patch.object(
        requests, "get"
    ) as fake_get_request, patch.object(requests, "post") as fake_post_request:
        client.get("/login")
        with client.session_transaction() as sess:
            nonce = sess["nonce"]

            redirect_url = "{endpoint}?response_type=code&client_id={client_id}&scope={scope}&state={state}".format(
                endpoint=app.config["OAUTH_AUTHORIZATION_ENDPOINT"],
                client_id=app.config["OAUTH_CLIENT_ID"],
                scope=scope,
                state=nonce,
            )

        r = client.get("/oauth", follow_redirects=False)
        assert r.location == redirect_url

        fake_post_response = Mock()
        fake_post_request.return_value = fake_post_response
        fake_post_response.status_code = 200
        fake_post_response.json = lambda: {"access_token": "fake_mlc_access_token"}

        fake_get_response = Mock()
        fake_get_request.return_value = fake_get_response
        fake_get_response.status_code = 200
        fake_get_response.json = lambda: {
            "id": oauth_id,
            "name": name,
            "email": email,
            "team": {"id": team_oauth_id, "name": team_name},
        }

        client.get(
            "/redirect?code={code}&state={state}".format(
                code="mlc_test_code", state=nonce
            ),
            follow_redirects=False,
        )

        if raise_for_error:
            with client.session_transaction() as sess:
                assert sess["id"]
                assert sess["nonce"]
                assert sess["hash"]
        return client


def get_scores(user):
    r = user.get("/api/v1/scoreboard")
    scores = r.get_json()
    return scores["data"]


def random_string(n=5):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(n)
    )


def random_int(start=2147483647, stop=None, step=1):
    return random.randrange(start, stop, step)


def gen_challenge(
    db,
    name="chal_name",
    description="chal_description",
    value=100,
    category="chal_category",
    type="standard",
    state="visible",
    **kwargs
):
    chal = Challenges(
        name=name,
        description=description,
        value=value,
        category=category,
        type=type,
        state=state,
        **kwargs
    )
    db.session.add(chal)
    db.session.commit()
    clear_challenges()
    return chal


def gen_award(db, user_id, team_id=None, name="award_name", value=100):
    award = Awards(user_id=user_id, team_id=team_id, name=name, value=value)
    award.date = datetime.datetime.utcnow()
    db.session.add(award)
    db.session.commit()
    clear_standings()
    return award


def gen_tag(db, challenge_id, value="tag_tag", **kwargs):
    tag = Tags(challenge_id=challenge_id, value=value, **kwargs)
    db.session.add(tag)
    db.session.commit()
    return tag


def gen_topic(db, challenge_id, value="topic", **kwargs):
    topic = Topics(value=value, **kwargs)
    db.session.add(topic)
    db.session.commit()

    challenge_topic = ChallengeTopics(challenge_id=challenge_id, topic_id=topic.id)
    db.session.add(challenge_topic)
    db.session.commit()
    return challenge_topic


def gen_file(db, location, challenge_id=None, page_id=None):
    if challenge_id:
        f = ChallengeFiles(challenge_id=challenge_id, location=location)
    elif page_id:
        f = PageFiles(page_id=page_id, location=location)
    else:
        f = Files(location=location)
    db.session.add(f)
    db.session.commit()
    return f


def gen_flag(db, challenge_id, content="flag", type="static", data=None, **kwargs):
    flag = Flags(challenge_id=challenge_id, content=content, type=type, **kwargs)
    if data:
        flag.data = data
    db.session.add(flag)
    db.session.commit()
    return flag


def gen_user(
    db, name="user_name", email="user@examplectf.com", password="password", **kwargs
):
    user = Users(name=name, email=email, password=password, **kwargs)
    db.session.add(user)
    db.session.commit()
    return user


def gen_team(
    db,
    name="team_name",
    email="team@examplectf.com",
    password="password",
    member_count=4,
    **kwargs
):
    team = Teams(name=name, email=email, password=password, **kwargs)
    for i in range(member_count):
        name = "user-{}-{}".format(random_string(), str(i))
        user = gen_user(db, name=name, email=name + "@examplectf.com", team_id=team.id)
        if i == 0:
            team.captain_id = user.id
        team.members.append(user)
    db.session.add(team)
    db.session.commit()
    return team


def gen_hint(
    db, challenge_id, content="This is a hint", cost=0, type="standard", **kwargs
):
    hint = Hints(
        challenge_id=challenge_id, content=content, cost=cost, type=type, **kwargs
    )
    db.session.add(hint)
    db.session.commit()
    return hint


def gen_unlock(db, user_id, team_id=None, target=None, type="hints"):
    unlock = Unlocks(user_id=user_id, team_id=team_id, target=target, type=type)
    db.session.add(unlock)
    db.session.commit()
    return unlock


def gen_solve(
    db,
    user_id,
    team_id=None,
    challenge_id=None,
    ip="127.0.0.1",
    provided="rightkey",
    **kwargs
):
    solve = Solves(
        user_id=user_id,
        team_id=team_id,
        challenge_id=challenge_id,
        ip=ip,
        provided=provided,
        **kwargs
    )
    solve.date = datetime.datetime.utcnow()
    db.session.add(solve)
    db.session.commit()
    clear_standings()
    clear_challenges()
    return solve


def gen_fail(
    db,
    user_id,
    team_id=None,
    challenge_id=None,
    ip="127.0.0.1",
    provided="wrongkey",
    **kwargs
):
    fail = Fails(
        user_id=user_id,
        team_id=team_id,
        challenge_id=challenge_id,
        ip=ip,
        provided=provided,
        **kwargs
    )
    fail.date = datetime.datetime.utcnow()
    db.session.add(fail)
    db.session.commit()
    return fail


def gen_tracking(db, user_id=None, ip="127.0.0.1", **kwargs):
    tracking = Tracking(ip=ip, user_id=user_id, **kwargs)
    db.session.add(tracking)
    db.session.commit()
    return tracking


def gen_page(db, title, route, content, draft=False, auth_required=False, **kwargs):
    page = Pages(
        title=title,
        route=route,
        content=content,
        draft=draft,
        auth_required=auth_required,
        **kwargs
    )
    db.session.add(page)
    db.session.commit()
    return page


def gen_notification(db, title="title", content="content"):
    notif = Notifications(title=title, content=content)
    db.session.add(notif)
    db.session.commit()


def gen_token(db, type="user", user_id=None, expiration=None):
    token = Tokens(type=type, user_id=user_id, expiration=expiration)
    db.session.add(token)
    db.session.commit()
    return token


def gen_comment(db, content="comment", author_id=None, type="challenge", **kwargs):
    if type == "challenge":
        model = ChallengeComments
    elif type == "user":
        model = UserComments
    elif type == "team":
        model = TeamComments
    elif type == "page":
        model = PageComments
    else:
        model = Comments

    comment = model(content=content, author_id=author_id, type=type, **kwargs)
    db.session.add(comment)
    db.session.commit()
    return comment


def gen_field(
    db,
    name="CustomField",
    type="user",
    field_type="text",
    description="CustomFieldDescription",
    required=True,
    public=True,
    editable=True,
):
    field = Fields(
        name=name,
        type=type,
        field_type=field_type,
        description=description,
        required=required,
        public=public,
        editable=editable,
    )
    db.session.add(field)
    db.session.commit()
    return field


def gen_bracket(
    db,
    name="players",
    description="players who are part of the test",
    type="users",
):
    bracket = Brackets(
        name=name,
        description=description,
        type=type,
    )
    db.session.add(bracket)
    db.session.commit()


def simulate_user_activity(db, user):
    gen_tracking(db, user_id=user.id)
    gen_award(db, user_id=user.id)
    challenge = gen_challenge(db)
    flag = gen_flag(db, challenge_id=challenge.id)
    hint = gen_hint(db, challenge_id=challenge.id)

    for _ in range(5):
        gen_fail(db, user_id=user.id, challenge_id=challenge.id)

    gen_unlock(db, user_id=user.id, target=hint.id, type="hints")
    gen_solve(db, user_id=user.id, challenge_id=challenge.id, provided=flag.content)
