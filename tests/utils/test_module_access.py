from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_audience,
    gen_audience_member,
    gen_challenge,
    gen_flag,
    gen_module,
    gen_module_audience_access,
    login_as_user,
    register_user,
)


def _challenge_ids_for(client):
    r = client.get("/api/v1/challenges")
    assert r.status_code == 200
    return {c["id"] for c in r.get_json()["data"]}


def test_ungrouped_challenge_visible_to_everyone():
    app = create_ctfd()
    with app.app_context():
        ungrouped_id = gen_challenge(app.db, name="public").id
        register_user(app)
        with login_as_user(app) as client:
            assert ungrouped_id in _challenge_ids_for(client)
    destroy_ctfd(app)


def test_module_without_audience_link_invisible_to_users():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="locked").id
        hidden_id = gen_challenge(app.db, name="hidden", module_id=module_id).id
        register_user(app)
        with login_as_user(app) as client:
            ids = _challenge_ids_for(client)
            assert hidden_id not in ids
        with login_as_user(app, name="admin") as client:
            r = client.get("/api/v1/challenges?view=admin")
            assert hidden_id in {c["id"] for c in r.get_json()["data"]}
    destroy_ctfd(app)


def test_user_in_audience_sees_linked_module():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        audience_id = gen_audience(app.db, name="seceng").id
        gen_module_audience_access(app.db, module_id=module_id, audience_id=audience_id)
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id

        register_user(app)
        gen_audience_member(app.db, audience_id=audience_id, user_id=2)
        register_user(app, name="other", email="other@examplectf.com")

        with login_as_user(app) as client:
            assert chal_id in _challenge_ids_for(client)
        with login_as_user(app, name="other") as client:
            assert chal_id not in _challenge_ids_for(client)
    destroy_ctfd(app)


def test_submission_to_inaccessible_challenge_is_404():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        gen_flag(app.db, challenge_id=chal_id, content="flag")
        register_user(app)
        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/challenges/attempt",
                json={"challenge_id": chal_id, "submission": "flag"},
            )
            assert r.status_code == 404
    destroy_ctfd(app)


def test_detail_view_for_inaccessible_challenge_is_404():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/challenges/{}".format(chal_id))
            assert r.status_code == 404
    destroy_ctfd(app)
