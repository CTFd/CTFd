from CTFd.models import Brackets, Users
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_bracket,
    login_as_user,
    register_user,
)


def test_brackets_get_api():
    """Test that brackets API GET endpiont is behaving propertly"""
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


def test_brackets_post_api():
    """Test that brackets API POST endpiont is behaving propertly"""
    app = create_ctfd()
    with app.app_context():
        data = {
            "name": "testplayers",
            "description": "Test players bracket",
            "type": "users",
        }
        register_user(app)
        with login_as_user(app) as client:
            r = client.post("/api/v1/brackets", json=data)
            assert r.status_code == 403
            assert Brackets.query.count() == 0

        with login_as_user(app, name="admin") as client:
            r = client.post("/api/v1/brackets", json=data)
            assert r.status_code == 200
            assert Brackets.query.count() == 1
    destroy_ctfd(app)


def test_brackets_patch_api():
    """Test that brackets API PATCH endpiont is behaving propertly"""
    app = create_ctfd()
    with app.app_context():
        gen_bracket(app.db, name="players1")
        assert Brackets.query.count() == 1

        register_user(app, bracket_id=1)
        with login_as_user(app) as client:
            r = client.patch("/api/v1/brackets/1", json={"name": "newplayers"})
            assert r.status_code == 403
            assert Brackets.query.filter_by(id=1).first().name == "players1"

        with login_as_user(app, name="admin") as client:
            r = client.patch("/api/v1/brackets/1", json={"name": "newplayers"})
            assert r.status_code == 200
            assert Brackets.query.filter_by(id=1).first().name == "newplayers"
    destroy_ctfd(app)


def test_brackets_delete_api():
    """Test that brackets API DELETE endpiont is behaving propertly"""
    app = create_ctfd()
    with app.app_context():
        gen_bracket(app.db, name="players1")
        assert Brackets.query.count() == 1

        register_user(app, bracket_id=1)
        with login_as_user(app) as client:
            r = client.delete("/api/v1/brackets/1", json="")
            assert r.status_code == 403
            assert Brackets.query.count() == 1

        with login_as_user(app, name="admin") as client:
            r = client.delete("/api/v1/brackets/1", json="")
            print(r.get_json())
            assert r.status_code == 200
            assert Brackets.query.count() == 0
    destroy_ctfd(app)


def test_user_bracket_changing():
    """Test that admins can change user's brackets via the API"""
    app = create_ctfd()
    with app.app_context():
        gen_bracket(app.db, name="players1")
        gen_bracket(app.db, name="players2")
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
        with login_as_user(app, name="admin") as client:
            assert Users.query.filter_by(id=2).first().bracket_id == 1
            r = client.patch("/api/v1/users/2", json={"bracket_id": 2})
            assert r.status_code == 200
            assert Users.query.filter_by(id=2).first().bracket_id == 2
    destroy_ctfd(app)
