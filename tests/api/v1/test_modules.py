from CTFd.models import ModuleAudienceAccess, Modules
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_audience,
    gen_challenge,
    gen_module,
    login_as_user,
    register_user,
)


def test_modules_list_admin_only():
    app = create_ctfd()
    with app.app_context():
        gen_module(app.db, name="owasp")
        register_user(app)
        json_headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        with login_as_user(app) as client:
            r = client.get("/api/v1/modules", headers=json_headers)
            assert r.status_code == 403
        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/modules", headers=json_headers)
            assert r.status_code == 200
            assert r.get_json()["data"][0]["name"] == "owasp"
    destroy_ctfd(app)


def test_modules_crud():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        with login_as_user(app, name="admin") as client:
            r = client.post("/api/v1/modules", json={"name": "owasp"})
            assert r.status_code == 200
            module_id = r.get_json()["data"]["id"]
            assert Modules.query.count() == 1

            r = client.patch(
                "/api/v1/modules/{}".format(module_id), json={"name": "renamed"}
            )
            assert r.status_code == 200
            assert Modules.query.filter_by(id=module_id).first().name == "renamed"

            r = client.delete("/api/v1/modules/{}".format(module_id), json="")
            assert r.status_code == 200
            assert Modules.query.count() == 0
    destroy_ctfd(app)


def test_module_audience_link():
    app = create_ctfd()
    with app.app_context():
        audience_id = gen_audience(app.db, name="seceng").id
        module_id = gen_module(app.db, name="owasp").id
        register_user(app)
        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/modules/{}/audiences".format(module_id),
                json={"audience_id": audience_id},
            )
            assert r.status_code == 200
            assert ModuleAudienceAccess.query.count() == 1

            r = client.delete(
                "/api/v1/modules/{}/audiences/{}".format(module_id, audience_id),
                json="",
            )
            assert r.status_code == 200
            assert ModuleAudienceAccess.query.count() == 0
    destroy_ctfd(app)


def test_challenge_module_id_roundtrip():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        register_user(app)
        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/challenges/{}".format(chal_id))
            assert r.status_code == 200
            assert r.get_json()["data"]["module_id"] == module_id

            r = client.patch(
                "/api/v1/challenges/{}".format(chal_id), json={"module_id": None}
            )
            assert r.status_code == 200
    destroy_ctfd(app)
