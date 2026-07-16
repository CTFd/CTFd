from CTFd.models import AudienceMembers, Audiences
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_audience,
    login_as_user,
    register_user,
)


def test_audiences_list_admin_only():
    app = create_ctfd()
    with app.app_context():
        gen_audience(app.db, name="seceng")
        register_user(app)
        json_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        with login_as_user(app) as client:
            r = client.get("/api/v1/audiences", headers=json_headers)
            assert r.status_code == 403
        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/audiences", headers=json_headers)
            assert r.status_code == 200
            assert r.get_json()["data"][0]["name"] == "seceng"
    destroy_ctfd(app)


def test_audiences_crud():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        # POST as non-admin -> 403
        with login_as_user(app) as client:
            r = client.post("/api/v1/audiences", json={"name": "x"})
            assert r.status_code == 403

        with login_as_user(app, name="admin") as client:
            r = client.post("/api/v1/audiences", json={"name": "seceng"})
            assert r.status_code == 200
            audience_id = r.get_json()["data"]["id"]
            assert Audiences.query.count() == 1

            r = client.patch(
                "/api/v1/audiences/{}".format(audience_id), json={"name": "renamed"}
            )
            assert r.status_code == 200
            assert Audiences.query.filter_by(id=audience_id).first().name == "renamed"

            r = client.delete("/api/v1/audiences/{}".format(audience_id), json="")
            assert r.status_code == 200
            assert Audiences.query.count() == 0
    destroy_ctfd(app)


def test_audience_member_add_remove():
    app = create_ctfd()
    with app.app_context():
        audience_id = gen_audience(app.db, name="seceng").id
        register_user(app)  # creates user id=2 (admin is 1)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/audiences/{}/members".format(audience_id),
                json={"user_id": 2},
            )
            assert r.status_code == 200
            member_id = r.get_json()["data"]["id"]
            assert AudienceMembers.query.count() == 1

            r = client.post("/api/v1/audiences/{}/members".format(audience_id), json={})
            assert r.status_code == 400

            r = client.delete(
                "/api/v1/audiences/{}/members/{}".format(audience_id, member_id),
                json="",
            )
            assert r.status_code == 200
            assert AudienceMembers.query.count() == 0
    destroy_ctfd(app)
