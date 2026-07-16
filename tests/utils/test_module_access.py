from CTFd.models import SolutionFiles
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_audience,
    gen_audience_member,
    gen_challenge,
    gen_file,
    gen_flag,
    gen_hint,
    gen_module,
    gen_module_audience_access,
    gen_solution,
    gen_solve,
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


def test_solution_endpoints_for_inaccessible_challenge_are_404():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        solution_id = gen_solution(
            app.db,
            challenge_id=chal_id,
            content="module gated solution",
            state="visible",
        ).id
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/challenges/{}/solution".format(chal_id))
            assert r.status_code == 404

            r = client.post(
                "/api/v1/unlocks", json={"target": solution_id, "type": "solutions"}
            )
            assert r.status_code == 404

            r = client.get("/api/v1/solutions/{}".format(solution_id))
            assert r.status_code == 404
    destroy_ctfd(app)


def test_direct_hint_for_inaccessible_challenge_is_404():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        hint_id = gen_hint(app.db, challenge_id=chal_id, cost=0).id
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/api/v1/hints/{}".format(hint_id))
            assert r.status_code == 404
    destroy_ctfd(app)


def test_challenge_file_for_inaccessible_challenge_is_404():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        gen_file(app.db, location="secret.txt", challenge_id=chal_id)
        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/files/secret.txt")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_solution_file_for_inaccessible_challenge_is_404():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        solution_id = gen_solution(
            app.db,
            challenge_id=chal_id,
            content="module gated solution",
            state="visible",
        ).id
        app.db.session.add(
            SolutionFiles(solution_id=solution_id, location="solution-secret.txt")
        )
        app.db.session.commit()

        register_user(app)
        with login_as_user(app) as client:
            r = client.get("/files/solution-secret.txt")
            assert r.status_code == 404
    destroy_ctfd(app)


def test_challenge_subresources_for_inaccessible_challenge_are_404():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)
        with login_as_user(app) as client:
            r = client.get("/api/v1/challenges/{}/solves".format(chal_id))
            assert r.status_code == 404

            r = client.put(
                "/api/v1/challenges/{}/ratings".format(chal_id), json={"value": 1}
            )
            assert r.status_code == 404
    destroy_ctfd(app)


def test_module_audience_link_changes_clear_access_cache():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        audience_id = gen_audience(app.db, name="seceng").id
        chal_id = gen_challenge(app.db, name="x", module_id=module_id).id
        register_user(app)
        gen_audience_member(app.db, audience_id=audience_id, user_id=2)

        with login_as_user(app) as client:
            assert chal_id not in _challenge_ids_for(client)

        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/modules/{}/audiences".format(module_id),
                json={"audience_id": audience_id},
            )
            assert r.status_code == 200

        with login_as_user(app) as client:
            assert chal_id in _challenge_ids_for(client)

        with login_as_user(app, name="admin") as client:
            r = client.delete(
                "/api/v1/modules/{}/audiences/{}".format(module_id, audience_id),
                json=True,
            )
            assert r.status_code == 200

        with login_as_user(app) as client:
            assert chal_id not in _challenge_ids_for(client)
    destroy_ctfd(app)


def test_module_challenge_assignment_clears_challenge_cache():
    app = create_ctfd()
    with app.app_context():
        module_id = gen_module(app.db, name="owasp").id
        chal_id = gen_challenge(app.db, name="x").id
        register_user(app)

        with login_as_user(app) as client:
            assert chal_id in _challenge_ids_for(client)

        with login_as_user(app, name="admin") as client:
            r = client.post(
                "/api/v1/modules/{}/challenges".format(module_id),
                json={"challenge_id": chal_id},
            )
            assert r.status_code == 200

        with login_as_user(app) as client:
            assert chal_id not in _challenge_ids_for(client)
    destroy_ctfd(app)
