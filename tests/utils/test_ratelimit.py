from tests.helpers import create_ctfd, destroy_ctfd, register_user


def test_ratelimit_on_auth():
    """Test that ratelimiting function works properly"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with app.test_client() as client:
            r = client.get("/login")
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "password": "wrong_password",
                    "nonce": sess.get("nonce"),
                }
            for x in range(10):
                r = client.post("/login", data=data)
                assert r.status_code == 200

            for x in range(5):
                r = client.post("/login", data=data)
                assert r.status_code == 429
    destroy_ctfd(app)
