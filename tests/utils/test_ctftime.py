from CTFd.models import Solves
from CTFd.utils.dates import ctf_ended, ctf_started
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
            gen_flag(app.db, challenge_id=chal.id, content=u"flag")

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
            gen_flag(app.db, challenge_id=chal.id, content=u"flag")

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
            gen_flag(app.db, challenge_id=chal.id, content=u"flag")

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
            gen_flag(app.db, challenge_id=chal.id, content=u"flag")

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
