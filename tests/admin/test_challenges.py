from tests.helpers import *


def test_get_admin_challenges():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_get_admin_challenges_new():
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/challenges/new')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_create_new_challenge():
    """Test that an admin can create a challenge properly"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")

        challenge_data = {
            "name": "name",
            "category": "category",
            "description": "description",
            "value": 100,
            "state": "hidden",
            "type": "standard"
        }

        r = client.post('/api/v1/challenges', json=challenge_data)
        assert r.get_json().get('data')['id'] == 1
        r = client.get('/admin/challenges/1')
        assert r.status_code == 200
        r = client.get('/api/v1/challenges/1')
        assert r.get_json().get('data')['id'] == 1

    destroy_ctfd(app)


def test_hidden_challenge_is_reachable():
    """Test that hidden challenges are visible for admins"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="admin", password="password")
        chal = gen_challenge(app.db, state='hidden')
        flag = gen_flag(app.db, challenge_id=chal.id, content='flag')
        chal_id = chal.id

        assert Challenges.query.count() == 1

        r = client.get('/api/v1/challenges', json='')
        data = r.get_json().get('data')
        assert data == []

        r = client.get('/api/v1/challenges/1', json='')
        assert r.status_code == 200
        data = r.get_json().get('data')
        assert data['name'] == 'chal_name'

        data = {
            "submission": 'flag',
            "challenge_id": chal_id
        }

        r = client.post('/api/v1/challenges/attempt', json=data)
        assert r.status_code == 404

        r = client.post('/api/v1/challenges/attempt?preview=true', json=data)
        assert r.status_code == 200
        resp = r.get_json()['data']
        assert resp.get('status') == "correct"
    destroy_ctfd(app)
