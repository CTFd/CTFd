from CTFd.models import Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    login_as_user,
    register_user,
    simulate_user_activity,
)


def test_browse_admin_submissions():
    """Test that an admin can create a challenge properly"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="RegisteredUser")
        user = Users.query.filter_by(id=2).first()
        simulate_user_activity(app.db, user)

        admin = login_as_user(app, name="admin", password="password")

        # It's difficult to do better checks here becase we're just doing string search.
        # incorrect includes the word correct and the navbar has correct and incorrect in it
        r = admin.get("/admin/submissions")
        assert r.status_code == 200
        assert "RegisteredUser" in r.get_data(as_text=True)
        assert "correct" in r.get_data(as_text=True)
        assert "incorrect" in r.get_data(as_text=True)

        r = admin.get("/admin/submissions/correct")
        assert r.status_code == 200
        assert "RegisteredUser" in r.get_data(as_text=True)
        assert "correct" in r.get_data(as_text=True)

        r = admin.get("/admin/submissions/incorrect")
        assert r.status_code == 200
        assert "RegisteredUser" in r.get_data(as_text=True)

        r = admin.get("/admin/submissions/correct?field=challenge_id&q=1")
        assert r.status_code == 200
        assert "RegisteredUser" in r.get_data(as_text=True)
    destroy_ctfd(app)
