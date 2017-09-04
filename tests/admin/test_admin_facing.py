from tests.helpers import *
from CTFd.models import Teams
from CTFd.utils import get_config, set_config, override_template, sendmail, verify_email, ctf_started, ctf_ended
from freezegun import freeze_time
from mock import patch


def test_admin_panel():
    """Does the admin panel return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin')
        assert r.status_code == 302
        r = client.get('/admin/graphs')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_pages():
    """Does admin pages return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/pages')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_teams():
    """Does admin teams return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/teams')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_scoreboard():
    """Does admin scoreboard return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_chals():
    """Does admin chals return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/chals')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_statistics():
    """Does admin statistics return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/statistics')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admin_config():
    """Does admin config return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")
        r = client.get('/admin/config')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_admins_can_access_challenges_before_ctftime():
    '''Admins can see and solve challenges despite it being before ctftime'''
    app = create_ctfd()
    with app.app_context():
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')

        with freeze_time("2017-10-2"):
            client = login_as_user(app, name='admin', password='password')
            r = client.get('/chals')
            assert r.status_code == 200

            with client.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
        solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
        assert solve_count == 1
    destroy_ctfd(app)
