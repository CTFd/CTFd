from datetime import datetime as DateTime
from datetime import timezone as TimeZone

import pytest

from CTFd.models import Solves
from CTFd.utils.dates import (
    ctf_ended,
    ctf_started,
    isoformat,
    unix_time,
    unix_time_millis,
    unix_time_to_utc,
)
from CTFd.utils.modes import TEAMS_MODE
from tests.helpers import (
    create_ctfd,
    ctftime,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    gen_team,
    login_as_user,
    register_user,
)


def test_ctftime_prevents_accessing_challenges_before_ctf():
    """Test that the ctftime function prevents users from accessing challenges before the ctf"""
    app = create_ctfd()
    with app.app_context():
        with ctftime.init():
            register_user(app)
            chal = gen_challenge(app.db)
            chal_id = chal.id
            gen_flag(app.db, challenge_id=chal.id, content="flag")

            with ctftime.not_started():
                client = login_as_user(app)
                r = client.get("/challenges")
                assert r.status_code == 403

                with client.session_transaction() as sess:
                    data = {"key": "flag", "nonce": sess.get("nonce")}
                r = client.get("/api/v1/challenges/{}".format(chal_id), data=data)
                data = r.get_data(as_text=True)
                assert r.status_code == 403
            solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
            assert solve_count == 0
    destroy_ctfd(app)


def test_ctftime_redirects_to_teams_page_in_teams_mode_before_ctf():
    """
    Test that the ctftime function redirects users to the team creation page in teams mode before the ctf if the user
    has no team yet.
    """
    app = create_ctfd(user_mode=TEAMS_MODE)
    with app.app_context():
        with ctftime.init():
            register_user(app)
            chal = gen_challenge(app.db)
            gen_flag(app.db, challenge_id=chal.id, content="flag")

            with ctftime.not_started():
                client = login_as_user(app)
                r = client.get("/challenges")
                assert r.status_code == 302

            gen_team(app.db, name="test", password="password")
            with login_as_user(app) as client:
                r = client.get("/teams/join")
                assert r.status_code == 200
                with client.session_transaction() as sess:
                    data = {
                        "name": "test",
                        "password": "password",
                        "nonce": sess.get("nonce"),
                    }
                r = client.post("/teams/join", data=data)
                assert r.status_code == 302

            with ctftime.not_started():
                client = login_as_user(app)
                r = client.get("/challenges")
                assert r.status_code == 403
    destroy_ctfd(app)


def test_ctftime_allows_accessing_challenges_during_ctf():
    """Test that the ctftime function allows accessing challenges during the ctf"""
    app = create_ctfd()
    with app.app_context():
        with ctftime.init():
            register_user(app)
            chal = gen_challenge(app.db)
            chal_id = chal.id
            gen_flag(app.db, challenge_id=chal.id, content="flag")

            with ctftime.started():
                client = login_as_user(app)
                r = client.get("/challenges")
                assert r.status_code == 200

                with client.session_transaction() as sess:
                    data = {
                        "submission": "flag",
                        "challenge_id": chal_id,
                        "nonce": sess.get("nonce"),
                    }
                r = client.post("/api/v1/challenges/attempt", data=data)
                assert r.status_code == 200
            solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
            assert solve_count == 1
    destroy_ctfd(app)


def test_ctftime_prevents_accessing_challenges_after_ctf():
    """Test that the ctftime function prevents accessing challenges after the ctf"""
    app = create_ctfd()
    with app.app_context():
        with ctftime.init():

            register_user(app)
            chal = gen_challenge(app.db)
            chal_id = chal.id
            gen_flag(app.db, challenge_id=chal.id, content="flag")

            with ctftime.ended():
                client = login_as_user(app)
                r = client.get("/challenges")
                assert r.status_code == 403

                with client.session_transaction() as sess:
                    data = {
                        "submission": "flag",
                        "challenge_id": chal_id,
                        "nonce": sess.get("nonce"),
                    }
                r = client.post("/api/v1/challenges/attempt", data=data)
                assert r.status_code == 403
            solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
            assert solve_count == 0
    destroy_ctfd(app)


def test_ctf_started():
    """
    Tests that the ctf_started function returns the correct value
    :return:
    """
    app = create_ctfd()
    with app.app_context():
        assert ctf_started() is True

        with ctftime.init():

            with ctftime.not_started():
                ctf_started()
                assert ctf_started() is False

            with ctftime.started():
                assert ctf_started() is True

            with ctftime.ended():
                assert ctf_started() is True
    destroy_ctfd(app)


def test_ctf_ended():
    """
    Tests that the ctf_ended function returns the correct value
    """
    app = create_ctfd()
    with app.app_context():
        assert ctf_ended() is False
        with ctftime.init():

            with ctftime.not_started():
                assert ctf_ended() is False

            with ctftime.started():
                assert ctf_ended() is False

            with ctftime.ended():
                assert ctf_ended() is True
    destroy_ctfd(app)


def test_unix_time():
    """
    Tests that the unix_time function returns the correct value and fails gracefully for strange inputs
    """
    assert unix_time(DateTime(2017, 1, 1)) == 1483228800
    assert type(unix_time(DateTime(2017, 1, 1))) == int
    assert unix_time(None) is None
    assert unix_time("test") is None
    assert unix_time(1) is None


def test_unix_time_millis():
    """
    Tests that the unix_time function returns the correct value and fails gracefully for strange inputs
    """
    # Aware datetime object
    assert unix_time_millis(DateTime(2017, 1, 1)) == 1483228800000
    assert type(unix_time_millis(DateTime(2017, 1, 1))) == int
    assert unix_time_millis(None) is None
    assert unix_time_millis("test") is None
    assert unix_time_millis(1) is None


def test_unix_time_to_utc():
    """
    Tests that the unix_time function returns the correct value and fails gracefully for strange inputs
    """
    assert unix_time_to_utc(0) == DateTime(1970, 1, 1)
    assert unix_time_to_utc(1483228800) == DateTime(2017, 1, 1)
    assert type(unix_time_to_utc(1483228800)) == DateTime
    assert unix_time_to_utc(None) is None
    with pytest.raises(TypeError):
        unix_time_to_utc("test")
    with pytest.raises(TypeError):
        unix_time_to_utc(DateTime(2017, 1, 1))


def test_isoformat():
    """
    Tests that the unix_time function returns the correct value and fails gracefully for strange inputs
    """
    assert (
        isoformat(DateTime(2017, 1, 1, tzinfo=TimeZone.utc))
        == "2017-01-01T00:00:00+00:00Z"
    )
    assert isoformat(DateTime(2017, 1, 1)) == "2017-01-01T00:00:00Z"
    assert isoformat(DateTime(2017, 1, 1, tzinfo=None)) == "2017-01-01T00:00:00Z"
    assert isoformat(None) is None
    assert isoformat("test") is None
    assert isoformat(1) is None
