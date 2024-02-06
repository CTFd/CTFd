from tests.helpers import create_ctfd, destroy_ctfd, gen_bracket, login_as_user


def test_get_brackets_api():
    """Test that brackets API endpiont is behaving propertly"""
    app = create_ctfd()
    with app.app_context():
        gen_bracket(app.db, name="players1")
        with app.test_client() as client:
            client.get("/register")
            with client.session_transaction() as sess:
                data = {
                    "name": "user",
                    "email": "user@examplectf.com",
                    "password": "password",
                    "bracket_id": 1,
                    "nonce": sess.get("nonce"),
                }
            client.post("/register", data=data)
            client = login_as_user(app, raise_for_error=True)
            r = client.get("/api/v1/brackets?type=users")
            resp = r.get_json()
            print(resp)
            assert r.status_code == 200
            assert resp["data"][0]["name"] == "players1"
            assert resp["data"][0]["description"] == "players who are part of the test"
    destroy_ctfd(app)
