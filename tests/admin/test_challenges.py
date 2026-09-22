import datetime

from CTFd.models import Challenges
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_flag,
    gen_module,
    login_as_user,
    register_user,
)


def _future():
    return datetime.datetime.utcnow() + datetime.timedelta(days=1)


def test_create_new_challenge():
    """Test that an admin can create a challenge properly"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "state": "hidden",
            "type": "standard",
        }

        r = client.post("/api/v1/challenges", json=challenge_data)
        assert r.get_json().get("data")["id"] == 1
        r = client.get("/admin/challenges/1")
        assert r.status_code == 200
        r = client.get("/api/v1/challenges/1")
        assert r.get_json().get("data")["id"] == 1

    destroy_ctfd(app)


def test_hidden_challenge_is_reachable():
    """Test that hidden challenges are visible for admins"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        chal = gen_challenge(app.db, state="hidden")
        gen_flag(app.db, challenge_id=chal.id, content="flag")
        chal_id = chal.id

        assert Challenges.query.count() == 1

        r = client.get("/api/v1/challenges", json="")
        data = r.get_json().get("data")
        assert data == []

        r = client.get("/api/v1/challenges/1", json="")
        assert r.status_code == 200
        data = r.get_json().get("data")
        assert data["name"] == "chal_name"

        data = {"submission": "flag", "challenge_id": chal_id}

        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 404

        r = client.post("/api/v1/challenges/attempt?preview=true", json=data)
        assert r.status_code == 200
        resp = r.get_json()["data"]
        assert resp.get("status") == "correct"
    destroy_ctfd(app)


def test_challenges_admin_only_as_user():
    app = create_ctfd()
    with app.app_context():
        set_config("challenge_visibility", "admins")

        register_user(app)
        client = login_as_user(app)

        gen_challenge(app.db)
        gen_flag(app.db, challenge_id=1, content="flag")

        r = client.get("/challenges")
        assert r.status_code == 403

        r = client.get("/api/v1/challenges", json="")
        assert r.status_code == 403

        r = client.get("/api/v1/challenges/1", json="")
        assert r.status_code == 403

        data = {"submission": "flag", "challenge_id": 1}
        r = client.post("/api/v1/challenges/attempt", json=data)
        assert r.status_code == 403
    destroy_ctfd(app)


def test_admin_challenges_listing_shows_scheduled_badge():
    """The admin challenge listing badges a not-yet-released challenge as scheduled"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db, name="later", state="visible", scheduled_at=_future())
        with login_as_user(app, "admin") as admin:
            r = admin.get("/admin/challenges")
            assert r.status_code == 200
            html = r.get_data(as_text=True)
            assert "badge-warning" in html
            assert "scheduled" in html
            assert "Becomes visible to users at" in html
    destroy_ctfd(app)


def test_admin_challenges_listing_warns_schedule_does_not_unhide():
    """The admin challenge listing warns that a schedule will not unhide a challenge"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db, name="later", state="hidden", scheduled_at=_future())
        with login_as_user(app, "admin") as admin:
            html = admin.get("/admin/challenges").get_data(as_text=True)
            assert "will not make it visible" in html
            assert "badge-warning" not in html
            # The release time is irrelevant for a hidden challenge, so the
            # tooltip states the rule without it
            assert "data-schedule-time" not in html
            assert "{time}" not in html
    destroy_ctfd(app)


def test_admin_challenges_listing_has_no_schedule_tooltip_without_schedule():
    """Challenges without a schedule keep their plain state badge"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db, name="plain", state="visible")
        with login_as_user(app, "admin") as admin:
            html = admin.get("/admin/challenges").get_data(as_text=True)
            assert "data-schedule-time" not in html
            assert "badge-success" in html
    destroy_ctfd(app)


def test_admin_challenge_detail_shows_scheduled_badge():
    """The admin challenge detail page badges a not-yet-released challenge as scheduled"""
    app = create_ctfd()
    with app.app_context():
        chal_id = gen_challenge(
            app.db, name="later", state="visible", scheduled_at=_future()
        ).id
        with login_as_user(app, "admin") as admin:
            html = admin.get(f"/admin/challenges/{chal_id}").get_data(as_text=True)
            assert "badge-warning" in html
            assert "Becomes visible to users at" in html
    destroy_ctfd(app)


def test_admin_module_detail_shows_scheduled_badge():
    """The admin module detail page badges a not-yet-released challenge as scheduled"""
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="Week 1").id
        gen_challenge(
            app.db,
            name="later",
            state="visible",
            scheduled_at=_future(),
            module_id=module_id,
        )
        with login_as_user(app, "admin") as admin:
            html = admin.get(f"/admin/modules/{module_id}").get_data(as_text=True)
            assert "badge-warning" in html
            assert "Becomes visible to users at" in html
    destroy_ctfd(app)
