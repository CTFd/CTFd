#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import set_config
from tests.helpers import *
from freezegun import freeze_time


def test_api_challenges_get_visibility_public():
    """Can a public user get /api/v1/challenges if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        set_config('challenge_visibility', 'public')
        with app.test_client() as client:
            r = client.get('/api/v1/challenges')
            assert r.status_code == 200
            set_config('challenge_visibility', 'private')
            r = client.get('/api/v1/challenges', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenges_get_ctftime_public():
    """Can a public user get /api/v1/challenges if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config('challenge_visibility', 'public')
        with app.test_client() as client:
            r = client.get('/api/v1/challenges')
            assert r.status_code == 200
            set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
            set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
            r = client.get('/api/v1/challenges')
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenges_get_visibility_private():
    """Can a private user get /api/v1/challenges if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges')
        assert r.status_code == 200
        set_config('challenge_visibility', 'public')
        r = client.get('/api/v1/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_get_ctftime_private():
    """Can a private user get /api/v1/challenges if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges')
        assert r.status_code == 200
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        r = client.get('/api/v1/challenges')
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenges_get_verified_emails():
    """Can a verified email user get /api/v1/challenges"""
    app = create_ctfd()
    with app.app_context():
        set_config('verify_emails', True)
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges', json="")
        assert r.status_code == 403
        gen_user(app.db, name='user_name', email='verified_user@ctfd.io', password='password', verified=True)
        registered_client = login_as_user(app, 'user_name', 'password')
        r = registered_client.get('/api/v1/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_post_non_admin():
    """Can a user post /api/v1/challenges if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.post('/api/v1/challenges', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenges_post_admin():
    """Can a user post /api/v1/challenges if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, 'admin') as client:
            r = client.post('/api/v1/challenges', json={
                "name": "chal",
                "category": "cate",
                "description": "desc",
                "value": "100",
                "state": "hidden",
                "type": "standard"})
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_types_post_non_admin():
    """Can a non-admin get /api/v1/challenges/types if not admin"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/types', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_types_post_admin():
    """Can an admin get /api/v1/challenges/types if admin"""
    app = create_ctfd()
    with app.app_context():
        with login_as_user(app, 'admin') as client:
            r = client.get('/api/v1/challenges/types', json="")
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_visibility_public():
    """Can a public user get /api/v1/challenges/<challenge_id> if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        set_config('challenge_visibility', 'public')
        with app.test_client() as client:
            gen_challenge(app.db)
            r = client.get('/api/v1/challenges/1')
            assert r.status_code == 200
            set_config('challenge_visibility', 'private')
            r = client.get('/api/v1/challenges/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_ctftime_public():
    """Can a public user get /api/v1/challenges/<challenge_id> if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config('challenge_visibility', 'public')
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/1')
            assert r.status_code == 200
            set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
            set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
            r = client.get('/api/v1/challenges/1')
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_visibility_private():
    """Can a private user get /api/v1/challenges/<challenge_id> if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 200
        set_config('challenge_visibility', 'public')
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_ctftime_private():
    """Can a private user get /api/v1/challenges/<challenge_id> if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 200
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_verified_emails():
    """Can a verified email load /api/v1/challenges/<challenge_id>"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        set_config('verify_emails', True)
        gen_challenge(app.db)
        gen_user(app.db, name='user_name', email='verified_user@ctfd.io', password='password', verified=True)
        register_user(app)
        client = login_as_user(app)
        registered_client = login_as_user(app, 'user_name', 'password')
        r = client.get('/api/v1/challenges/1', json="")
        assert r.status_code == 403
        r = registered_client.get('/api/v1/challenges/1')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_non_existing():
    """Will a bad <challenge_id> at /api/v1/challenges/<challenge_id> 404"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-5"):
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges/1')
        assert r.status_code == 404
    destroy_ctfd(app)


def test_api_challenge_patch_non_admin():
    """Can a user patch /api/v1/challenges/<challenge_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.patch('/api/v1/challenges/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_patch_admin():
    """Can a user patch /api/v1/challenges/<challenge_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, 'admin') as client:
            r = client.patch('/api/v1/challenges/1', json={
                "name": "chal_name",
                "value": "200"})
            assert r.status_code == 200
            assert r.get_json()['data']['value'] == 200
    destroy_ctfd(app)


def test_api_challenge_delete_non_admin():
    """Can a user delete /api/v1/challenges/<challenge_id> if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.delete('/api/v1/challenges/1', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_delete_admin():
    """Can a user patch /api/v1/challenges/<challenge_id> if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, 'admin') as client:
            r = client.delete('/api/v1/challenges/1', json="")
            assert r.status_code == 200
            assert r.get_json().get('data') is None
    destroy_ctfd(app)


def test_api_challenge_attempt_post_public():
    """Can a public user post /api/v1/challenges/attempt"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.post('/api/v1/challenges/attempt', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_attempt_post_private():
    """Can an private user post /api/v1/challenges/attempt"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_flag(app.db, 1)
        register_user(app)
        with login_as_user(app) as client:
            r = client.post('/api/v1/challenges/attempt', json={"challenge_id": 1, "submission": "wrong_flag"})
            assert r.status_code == 200
            assert r.get_json()['data']['status'] == 'incorrect'
            r = client.post('/api/v1/challenges/attempt', json={"challenge_id": 1, "submission": "flag"})
            assert r.status_code == 200
            assert r.get_json()['data']['status'] == 'correct'
            r = client.post('/api/v1/challenges/attempt', json={"challenge_id": 1, "submission": "flag"})
            assert r.status_code == 200
            assert r.get_json()['data']['status'] == 'already_solved'
    destroy_ctfd(app)


def test_api_challenge_attempt_post_admin():
    """Can an admin user post /api/v1/challenges/attempt"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        gen_flag(app.db, 1)
        with login_as_user(app, 'admin') as client:
            r = client.post('/api/v1/challenges/attempt', json={"challenge_id": 1, "submission": "wrong_flag"})
            assert r.status_code == 200
            assert r.get_json()['data']['status'] == 'incorrect'
            r = client.post('/api/v1/challenges/attempt', json={"challenge_id": 1, "submission": "flag"})
            assert r.status_code == 200
            assert r.get_json()['data']['status'] == 'correct'
            r = client.post('/api/v1/challenges/attempt', json={"challenge_id": 1, "submission": "flag"})
            assert r.status_code == 200
            assert r.get_json()['data']['status'] == 'already_solved'
    destroy_ctfd(app)


def test_api_challenge_get_solves_visibility_public():
    """Can a public user get /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            set_config('challenge_visibility', 'public')
            r = client.get('/api/v1/challenges/1/solves', json="")
            assert r.status_code == 200
            set_config('challenge_visibility', 'private')
            r = client.get('/api/v1/challenges/1/solves', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_solves_ctftime_public():
    """Can a public user get /api/v1/challenges/<challenge_id>/solves if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        set_config('challenge_visibility', 'public')
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/1/solves')
            assert r.status_code == 200
            set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
            set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
            r = client.get('/api/v1/challenges/1/solves', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_solves_visibility_private():
    """Can a private user get /api/v1/challenges/<challenge_id>/solves if challenge_visibility is private/public"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
        set_config('challenge_visibility', 'public')
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_solves_ctftime_private():
    """Can a private user get /api/v1/challenges/<challenge_id>/solves if ctftime is over"""
    app = create_ctfd()
    with app.app_context(), freeze_time("2017-10-7"):
        gen_challenge(app.db)
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_solves_verified_emails():
    """Can a verified email get /api/v1/challenges/<challenge_id>/solves"""
    app = create_ctfd()
    with app.app_context():
        set_config('verify_emails', True)
        gen_challenge(app.db)
        gen_user(app.db, name='user_name', email='verified_user@ctfd.io', password='password', verified=True)
        register_user(app)
        client = login_as_user(app)
        registered_client = login_as_user(app, 'user_name', 'password')
        r = client.get('/api/v1/challenges/1/solves', json="")
        assert r.status_code == 403
        r = registered_client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenges_get_solves_score_visibility():
    """Can a user get /api/v1/challenges/<challenge_id>/solves if score_visibility is public/private/admin"""
    app = create_ctfd()
    with app.app_context():
        set_config('challenge_visibility', 'public')
        set_config('score_visibility', 'public')
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/1/solves')
            assert r.status_code == 200
        set_config('challenge_visibility', 'private')
        set_config('score_visibility', 'private')
        register_user(app)
        private_client = login_as_user(app)
        r = private_client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
        set_config('score_visibility', 'admin')
        admin = login_as_user(app, 'admin', 'password')
        r = admin.get('/api/v1/challenges/1/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_solves_404():
    """Will a bad <challenge_id> at /api/v1/challenges/<challenge_id>/solves 404"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/api/v1/challenges/1/solves')
        assert r.status_code == 404
    destroy_ctfd(app)


def test_api_challenge_solves_returns_correct_data():
    """Test that /api/v1/<challenge_id>/solves returns expected data"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_solve(app.db, user_id=2, challenge_id=chal.id)
        r = client.get('/api/v1/challenges/1/solves')
        resp = r.get_json()['data']
        solve = resp[0]
        assert r.status_code == 200
        assert solve.get('account_id') == 2
        assert solve.get('name') == 'user'
        assert solve.get('date') is not None
        assert solve.get('account_url') == '/users/2'
    destroy_ctfd(app)

    app = create_ctfd(user_mode="teams")
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        team = gen_team(app.db)
        user = Users.query.filter_by(id=2).first()
        user.team_id = team.id
        app.db.session.commit()
        chal = gen_challenge(app.db)
        gen_solve(app.db, user_id=2, team_id=1, challenge_id=chal.id)
        r = client.get('/api/v1/challenges/1/solves')
        resp = r.get_json()['data']
        solve = resp[0]
        assert r.status_code == 200
        assert solve.get('account_id') == 1
        assert solve.get('name') == 'team_name'
        assert solve.get('date') is not None
        assert solve.get('account_url') == '/teams/1'
    destroy_ctfd(app)

    app = create_ctfd(application_root='/ctf')
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        gen_solve(app.db, user_id=2, challenge_id=chal.id)
        r = client.get('/api/v1/challenges/1/solves')
        resp = r.get_json()['data']
        solve = resp[0]
        assert r.status_code == 200
        assert solve.get('account_id') == 2
        assert solve.get('name') == 'user'
        assert solve.get('date') is not None
        assert solve.get('account_url') == '/ctf/users/2'
    destroy_ctfd(app)


def test_api_challenge_get_files_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/files if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/1/files', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_files_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/files if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, 'admin') as client:
            r = client.get('/api/v1/challenges/1/files')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_tags_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/tags if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/1/tags', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_tags_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/tags if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, 'admin') as client:
            r = client.get('/api/v1/challenges/1/tags')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_hints_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/hints if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/1/hints', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_hints_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/hints if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, 'admin') as client:
            r = client.get('/api/v1/challenges/1/hints')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_api_challenge_get_flags_non_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/flags if not admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with app.test_client() as client:
            r = client.get('/api/v1/challenges/1/flags', json="")
            assert r.status_code == 403
    destroy_ctfd(app)


def test_api_challenge_get_flags_admin():
    """Can a user get /api/v1/challenges/<challenge_id>/flags if admin"""
    app = create_ctfd()
    with app.app_context():
        gen_challenge(app.db)
        with login_as_user(app, 'admin') as client:
            r = client.get('/api/v1/challenges/1/flags')
            assert r.status_code == 200
    destroy_ctfd(app)
