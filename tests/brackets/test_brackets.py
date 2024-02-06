from CTFd.models import Teams, Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_bracket,
    login_as_user,
    register_team,
    register_user,
)


def test_require_bracket_on_register():
    """Require users to submit a bracket if there is a bracket configured"""
    app = create_ctfd()
    with app.app_context():
        gen_bracket(app.db)
        with app.test_client() as client:
            client.get("/register")
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "email": "user@examplectf.com",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            client.post("/register", data=data)
            login_as_user(app, raise_for_error=False)
            assert Users.query.filter_by(email="user@examplectf.com").count() == 0
            data["bracket_id"] = 1
            client.post("/register", data=data)
            login_as_user(app, raise_for_error=True)
            assert Users.query.filter_by(email="user@examplectf.com").count() == 1
    destroy_ctfd(app)


def test_require_team_bracket_on_register():
    """Test that brackets are required on team mode"""
    app = create_ctfd(user_mode="teams")
    with app.app_context():
        gen_bracket(app.db, type="teams")
        register_user(app)
        with login_as_user(app) as client:
            register_team(app, raise_for_error=False)

            with client.session_transaction() as sess:
                data = {
                    "name": "team",
                    "password": "password",
                    "nonce": sess.get("nonce"),
                }
            # Test that a team is not created
            client.post("/teams/new", data=data)
            assert Teams.query.count() == 0

            # Test that the team is now created
            data["bracket_id"] = 1
            client.post("/teams/new", data=data)
            assert Teams.query.filter_by(id=1).first().bracket_id == 1
    destroy_ctfd(app)
