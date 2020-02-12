from freezegun import freeze_time

from CTFd.models import Solves
from CTFd.utils import set_config
from CTFd.utils.dates import ctf_ended, ctf_started
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    login_as_user,
    register_user,
)


def test_ctftime_prevents_accessing_challenges_before_ctf():
    """Test that the ctftime function prevents users from accessing challenges before the ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        gen_flag(app.db, challenge_id=chal.id, content=u"flag")

        with freeze_time("2017-10-3"):  # CTF has not started yet.
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


def test_ctftime_allows_accessing_challenges_during_ctf():
    """Test that the ctftime function allows accessing challenges during the ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        gen_flag(app.db, challenge_id=chal.id, content=u"flag")

        with freeze_time("2017-10-5"):
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
        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        gen_flag(app.db, challenge_id=chal.id, content=u"flag")

        with freeze_time("2017-10-7"):
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

        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-10-3"):
            ctf_started()
            assert ctf_started() is False

        with freeze_time("2017-10-5"):
            assert ctf_started() is True

        with freeze_time("2017-10-7"):
            assert ctf_started() is True
    destroy_ctfd(app)


def test_ctf_ended():
    """
    Tests that the ctf_ended function returns the correct value
    """
    app = create_ctfd()
    with app.app_context():
        assert ctf_ended() is False

        set_config(
            "start", "1507089600"
        )  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config(
            "end", "1507262400"
        )  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-10-3"):
            assert ctf_ended() is False

        with freeze_time("2017-10-5"):
            assert ctf_ended() is False

        with freeze_time("2017-10-7"):
            assert ctf_ended() is True
    destroy_ctfd(app)
