import datetime

from CTFd.models import SolutionFiles, Unlocks
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_file,
    gen_hint,
    gen_solution,
    login_as_user,
    register_user,
)


def _future():
    return datetime.datetime.utcnow() + datetime.timedelta(days=1)


def test_challenge_file_for_scheduled_challenge_is_404():
    """Non-admins cannot download challenge files before scheduled_at"""
    app = create_ctfd()
    with app.app_context():
        chal_id = gen_challenge(app.db, scheduled_at=_future()).id
        gen_file(app.db, location="secret.txt", challenge_id=chal_id)
        register_user(app)
        with login_as_user(app) as client:
            assert client.get("/files/secret.txt").status_code == 404
        with login_as_user(app, "admin") as admin:
            # Admin download hits storage (file not really on disk) -> 404 from IOError,
            # so we only assert it is not blocked by the scheduled_at gate (not 403).
            assert admin.get("/files/secret.txt").status_code != 403
    destroy_ctfd(app)


def test_solution_file_for_scheduled_challenge_is_404():
    """Non-admins cannot download solution files before scheduled_at"""
    app = create_ctfd()
    with app.app_context():
        chal_id = gen_challenge(app.db, scheduled_at=_future()).id
        solution_id = gen_solution(
            app.db,
            challenge_id=chal_id,
            content="scheduled solution",
            state="visible",
        ).id
        app.db.session.add(
            SolutionFiles(solution_id=solution_id, location="solution-secret.txt")
        )
        app.db.session.commit()

        register_user(app)
        with login_as_user(app) as client:
            assert client.get("/files/solution-secret.txt").status_code == 404
    destroy_ctfd(app)


def test_unlock_hint_for_scheduled_challenge_is_404():
    """Non-admins cannot unlock hints for a future-scheduled challenge"""
    app = create_ctfd()
    with app.app_context():
        chal_id = gen_challenge(app.db, scheduled_at=_future()).id
        hint_id = gen_hint(app.db, challenge_id=chal_id, content="secret", cost=0).id
        register_user(app)
        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/unlocks",
                json={"target": hint_id, "type": "hints"},
            )
            assert r.status_code == 404
            assert Unlocks.query.count() == 0
    destroy_ctfd(app)


def test_unlock_solution_for_scheduled_challenge_is_404():
    """Non-admins cannot unlock solutions for a future-scheduled challenge"""
    app = create_ctfd()
    with app.app_context():
        chal_id = gen_challenge(app.db, scheduled_at=_future()).id
        solution_id = gen_solution(
            app.db, challenge_id=chal_id, content="secret", state="visible"
        ).id
        register_user(app)
        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/unlocks",
                json={"target": solution_id, "type": "solutions"},
            )
            assert r.status_code == 404
            assert Unlocks.query.count() == 0
    destroy_ctfd(app)
