from CTFd.models import Users
from CTFd.utils import set_config
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    login_as_user,
    register_user,
    simulate_user_activity,
)


def test_admins_can_see_scores_with_hidden_scores():
    """Test that admins can see user scores when Score Visibility is set to hidden"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        user = Users.query.filter_by(id=2).first()
        simulate_user_activity(app.db, user=user)

        admin = login_as_user(app, name="admin", password="password")
        user = login_as_user(app)

        set_config("score_visibility", "hidden")

        # Users can see their own data
        r = user.get("/api/v1/users/me/fails", json="")
        assert r.status_code == 200
        r = user.get("/api/v1/users/me/solves", json="")
        assert r.status_code == 200

        # Users cannot see public data
        r = user.get("/api/v1/users/2/solves", json="")
        assert r.status_code == 403
        r = user.get("/api/v1/users/2/fails", json="")
        assert r.status_code == 403
        r = user.get("/scoreboard")
        assert r.status_code == 403
        r = user.get("/api/v1/scoreboard", json="")
        assert r.status_code == 403

        # Admins can see user data
        r = admin.get("/api/v1/users/2/fails", json="")
        assert r.status_code != 403

        # Admins can see the scoreboard
        r = admin.get("/scoreboard")
        assert r.status_code != 403
        assert "Scores are not currently visible to users" in r.get_data(as_text=True)

        # Admins can see the scoreboard
        r = admin.get("/api/v1/scoreboard", json="")
        assert r.status_code != 403

    destroy_ctfd(app)
