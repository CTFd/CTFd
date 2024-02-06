from tests.helpers import create_ctfd, destroy_ctfd, gen_bracket, login_as_user
from CTFd.models import Users

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
