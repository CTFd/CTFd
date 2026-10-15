from CTFd.models import Tracking
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    login_as_user,
    register_user,
)


def test_tracking_records_user_agent():
    """Test that Tracking stores the user agent alongside the IP address"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app) as client:
            client.get("/challenges", headers={"User-Agent": "Browser/1.0"})

        assert (
            Tracking.query.filter_by(user_id=2, user_agent="Browser/1.0").count() == 1
        )
    destroy_ctfd(app)


def test_tracking_new_user_agent_creates_new_entry():
    """Test that the same IP with a different user agent is tracked separately and user agents are truncated to 256 characters"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        long_user_agent = "A" * 1000
        with login_as_user(app) as client:
            client.get("/challenges", headers={"User-Agent": "Browser/1.0"})
            client.get("/challenges", headers={"User-Agent": "Browser/1.0"})
            client.get("/challenges", headers={"User-Agent": "Browser/2.0"})
            client.get("/challenges", headers={"User-Agent": long_user_agent})

        user_agents = {
            t.user_agent for t in Tracking.query.filter_by(user_id=2, type=None)
        }
        assert {"Browser/1.0", "Browser/2.0", "A" * 256} <= user_agents
        assert (
            Tracking.query.filter_by(user_id=2, user_agent="Browser/1.0").count() == 1
        )
        assert (
            Tracking.query.filter_by(user_id=2, user_agent="Browser/2.0").count() == 1
        )
        assert (
            Tracking.query.filter_by(user_id=2, user_agent="A" * 256).count() == 1
        )
    destroy_ctfd(app)


def test_tracking_challenge_open_records_user_agent():
    """Test that challenge open Tracking entries store the user agent"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        with login_as_user(app) as client:
            r = client.get(
                "/api/v1/challenges/1", headers={"User-Agent": "Browser/1.0"}
            )
            assert r.status_code == 200

        track = Tracking.query.filter_by(
            user_id=2, type="challenges.open", target=1
        ).first()
        assert track.user_agent == "Browser/1.0"
    destroy_ctfd(app)


def test_tracking_user_agent_exact_match():
    """Test that user agents differing only in case/accents/trailing spaces are tracked separately"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user_agents = ["Browser/1.0", "browser/1.0", "Browsér/1.0", "Browser/1.0 "]
        with login_as_user(app) as client:
            for _ in range(2):
                for user_agent in user_agents:
                    client.get("/challenges", headers={"User-Agent": user_agent})

        for user_agent in user_agents:
            tracks = [
                t
                for t in Tracking.query.filter_by(user_id=2, type=None).all()
                if t.user_agent == user_agent
            ]
            assert len(tracks) == 1
    destroy_ctfd(app)
