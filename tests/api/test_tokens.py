import datetime

from CTFd.exceptions import UserNotFoundException, UserTokenExpiredException
from CTFd.models import Tokens
from CTFd.utils.security.auth import generate_user_token, lookup_user_token
from tests.helpers import create_ctfd, destroy_ctfd, gen_token, gen_user


def test_generate_user_token():
    app = create_ctfd()
    with app.app_context():
        user = gen_user(app.db)
        token = generate_user_token(user, expiration=None)
        token.user_id == user.id
        assert token.expiration > datetime.datetime.utcnow()
        assert Tokens.query.count() == 1
    destroy_ctfd(app)


def test_lookup_user_token():
    app = create_ctfd()
    with app.app_context():
        user = gen_user(app.db)
        # Good Token
        token = gen_token(app.db, user_id=user.id)
        user = lookup_user_token(token.value)
        assert user.id == token.user_id

        # Expired Token
        expiration = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
        token = gen_token(app.db, user_id=user.id, expiration=expiration)
        try:
            lookup_user_token(token.value)
        except UserTokenExpiredException:
            pass
        except Exception as e:
            raise e

        # Nonexistant token
        try:
            lookup_user_token("wat")
        except UserNotFoundException:
            pass
        except Exception as e:
            raise e
    destroy_ctfd(app)


def test_user_token_access():
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get("/api/v1/users/me", json="")
            assert r.status_code == 403

        with app.test_client() as client:
            user = gen_user(app.db, name="user2", email="user2@ctfd.io")
            expiration = datetime.datetime.utcnow() + datetime.timedelta(days=-1)
            token = generate_user_token(user, expiration=expiration)
            headers = {"Authorization": "token " + token.value}
            r = client.get("/api/v1/users/me", headers=headers, json="")
            assert r.status_code == 401

        with app.test_client() as client:
            headers = {"Authorization": "token invalid_token"}
            r = client.get("/api/v1/users/me", headers=headers, json="")
            assert r.status_code == 401

        with app.test_client() as client:
            user = gen_user(app.db, name="user1", email="user1@ctfd.io")
            token = generate_user_token(user, expiration=None)
            headers = {"Authorization": "token " + token.value}
            r = client.get("/api/v1/users/me", headers=headers, json="")
            assert r.status_code == 200
            resp = r.get_json()
            assert resp["data"]["email"] == "user1@ctfd.io"
            assert resp["data"]["name"] == "user1"
    destroy_ctfd(app)
