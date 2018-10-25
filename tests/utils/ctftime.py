from tests.helpers import *
from CTFd.utils import get_config, set_config
from CTFd.utils.dates import ctf_started, ctf_ended
from freezegun import freeze_time
from mock import patch, Mock


def test_ctftime_prevents_accessing_challenges_before_ctf():
    """Test that the ctftime function prevents users from accessing challenges before the ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')

        with freeze_time("2017-10-3"):  # CTF has not started yet.
            client = login_as_user(app)
            r = client.get('/chals')
            assert r.status_code == 403

            with client.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            data = r.get_data(as_text=True)
            assert r.status_code == 403
        solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
        assert solve_count == 0
    destroy_ctfd(app)


def test_ctftime_allows_accessing_challenges_during_ctf():
    """Test that the ctftime function allows accessing challenges during the ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')

        with freeze_time("2017-10-5"):
            client = login_as_user(app)
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


def test_ctftime_prevents_accessing_challenges_after_ctf():
    """Test that the ctftime function prevents accessing challenges after the ctf"""
    app = create_ctfd()
    with app.app_context():
        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST
        register_user(app)
        chal = gen_challenge(app.db)
        chal_id = chal.id
        flag = gen_flag(app.db, chal=chal.id, flag=u'flag')

        with freeze_time("2017-10-7"):
            client = login_as_user(app)
            r = client.get('/chals')
            assert r.status_code == 403

            with client.session_transaction() as sess:
                data = {
                    "key": 'flag',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 403
        solve_count = app.db.session.query(app.db.func.count(Solves.id)).first()[0]
        assert solve_count == 0
    destroy_ctfd(app)


def test_ctf_started():
    '''Tests that the ctf_started function returns the correct value'''
    app = create_ctfd()
    with app.app_context():
        assert ctf_started() == True

        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-10-3"):
            assert ctf_started() == False

        with freeze_time("2017-10-5"):
            assert ctf_started() == True

        with freeze_time("2017-10-7"):
            assert ctf_started() == True
    destroy_ctfd(app)


def test_ctf_ended():
    '''Tests that the ctf_ended function returns the correct value'''
    app = create_ctfd()
    with app.app_context():
        assert ctf_ended() == False

        set_config('start', '1507089600')  # Wednesday, October 4, 2017 12:00:00 AM GMT-04:00 DST
        set_config('end', '1507262400')  # Friday, October 6, 2017 12:00:00 AM GMT-04:00 DST

        with freeze_time("2017-10-3"):
            assert ctf_ended() == False

        with freeze_time("2017-10-5"):
            assert ctf_ended() == False

        with freeze_time("2017-10-7"):
            assert ctf_ended() == True
    destroy_ctfd(app)
