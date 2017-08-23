#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.models import Teams, Solves, WrongKeys
from CTFd.utils import get_config, set_config
from CTFd import utils
from tests.helpers import *
from freezegun import freeze_time
from mock import patch
import json


def test_index():
    """Does the index page return a 200 by default"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_register_user():
    """Can a user be registered"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_register_unicode_user():
    """Can a user with a unicode name be registered"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="你好")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the created user
    destroy_ctfd(app)


def test_register_duplicate_teamname():
    """A user shouldn't be able to use an already registered team name"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        register_user(app, name="user1", email="user2@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the first created user
    destroy_ctfd(app)


def test_register_duplicate_email():
    """A user shouldn't be able to use an already registered email address"""
    app = create_ctfd()
    with app.app_context():
        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        register_user(app, name="user2", email="user1@ctfd.io", password="password")
        team_count = app.db.session.query(app.db.func.count(Teams.id)).first()[0]
        assert team_count == 2  # There's the admin user and the first created user
    destroy_ctfd(app)


def test_user_bad_login():
    """A user should not be able to login with an incorrect password"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app, name="user", password="wrong_password")
        r = client.get('/profile')
        assert r.location.startswith("http://localhost/login")  # We got redirected to login
    destroy_ctfd(app)


def test_user_login():
    """Can a registered user can login"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        assert r.location != "http://localhost/login"  # We didn't get redirected to login
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_isnt_admin():
    """A registered user cannot access admin pages"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/admin/graphs')
        assert r.location == "http://localhost/login"
        assert r.status_code == 302
    destroy_ctfd(app)


def test_user_get_teams():
    """Can a registered user load /teams"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/teams')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_scoreboard():
    """Can a registered user load /scoreboard"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/scoreboard')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_scores():
    """Can a registered user load /scores"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/scores')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_topteams():
    """Can a registered user load /top/10"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/top/10')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_challenges():
    """Can a registered user load /challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/challenges')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_chals():
    """Can a registered user load /chals"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/chals')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_solves_per_chal():
    """Can a registered user load /chals/solves"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/chals/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_solves():
    """Can a registered user load /solves"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/solves')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_team_page():
    """Can a registered user load their public profile (/team/2)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/team/2')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_profile():
    """Can a registered user load their private profile (/profile)"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        r = client.get('/profile')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_user_get_logout():
    """Can a registered user load /logout"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        client.get('/logout', follow_redirects=True)
        r = client.get('/challenges')
        assert r.location == "http://localhost/login?next=challenges"
        assert r.status_code == 302
    destroy_ctfd(app)


def test_user_get_reset_password():
    """Can an unregistered user load /reset_password"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = app.test_client()
        r = client.get('/reset_password')
        assert r.status_code == 200
    destroy_ctfd(app)


def test_viewing_challenges():
    """Test that users can see added challenges"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        gen_challenge(app.db)
        r = client.get('/chals')
        chals = json.loads(r.get_data(as_text=True))
        assert len(chals['game']) == 1
    destroy_ctfd(app)


def test_submitting_correct_flag():
    """Test that correct flags are correct"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 1 and resp.get('message') == "Correct"
    destroy_ctfd(app)


def test_submitting_incorrect_flag():
    """Test that incorrect flags are incorrect"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        with client.session_transaction() as sess:
            data = {
                "key": 'notflag',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 0 and resp.get('message') == "Incorrect"
    destroy_ctfd(app)


def test_submitting_unicode_flag():
    """Test that users can submit a unicode flag"""
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)
        chal = gen_challenge(app.db)
        flag = gen_flag(app.db, chal=chal.id, flag=u'你好')
        with client.session_transaction() as sess:
            data = {
                "key": '你好',
                "nonce": sess.get('nonce')
            }
        r = client.post('/chal/{}'.format(chal.id), data=data)
        assert r.status_code == 200
        resp = json.loads(r.data.decode('utf8'))
        assert resp.get('status') == 1 and resp.get('message') == "Correct"
    destroy_ctfd(app)


def test_submitting_flags_with_large_ips():
    '''Test that users with high octect IP addresses can submit flags'''
    app = create_ctfd()
    with app.app_context():
        register_user(app)
        client = login_as_user(app)

        # SQLite doesn't support BigInteger well so we can't test it properly
        ip_addresses = ['172.18.0.1', '255.255.255.255', '2001:0db8:85a3:0000:0000:8a2e:0370:7334']
        for ip_address in ip_addresses:
            # Monkeypatch get_ip
            utils.get_ip = lambda: ip_address

            # Generate challenge and flag
            chal = gen_challenge(app.db)
            chal_id = chal.id
            flag = gen_flag(app.db, chal=chal.id, flag=u'correct_key')

            # Submit wrong_key
            with client.session_transaction() as sess:
                data = {
                    "key": 'wrong_key',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
            resp = json.loads(r.data.decode('utf8'))
            assert resp.get('status') == 0 and resp.get('message') == "Incorrect"
            assert WrongKeys.query.filter_by(ip=ip_address).first()

            # Submit correct key
            with client.session_transaction() as sess:
                data = {
                    "key": 'correct_key',
                    "nonce": sess.get('nonce')
                }
            r = client.post('/chal/{}'.format(chal_id), data=data)
            assert r.status_code == 200
            resp = json.loads(r.data.decode('utf8'))
            assert resp.get('status') == 1 and resp.get('message') == "Correct"
            assert Solves.query.filter_by(ip=ip_address).first()
    destroy_ctfd(app)


def test_scoring_logic():
    """Test that scoring logic is correct"""
    app = create_ctfd()
    with app.app_context():
        admin = login_as_user(app, name="admin", password="password")

        register_user(app, name="user1", email="user1@ctfd.io", password="password")
        client1 = login_as_user(app, name="user1", password="password")
        register_user(app, name="user2", email="user2@ctfd.io", password="password")
        client2 = login_as_user(app, name="user2", password="password")

        chal1 = gen_challenge(app.db)
        flag1 = gen_flag(app.db, chal=chal1.id, flag='flag')
        chal1_id = chal1.id

        chal2 = gen_challenge(app.db)
        flag2 = gen_flag(app.db, chal=chal2.id, flag='flag')
        chal2_id = chal2.id

        # user1 solves chal1
        with client1.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
            r = client1.post('/chal/{}'.format(chal1_id), data=data)

        # user1 is now on top
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user1'

        # user2 solves chal1 and chal2
        with client2.session_transaction() as sess:
            # solve chal1
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
            r = client2.post('/chal/{}'.format(chal1_id), data=data)
            # solve chal2
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
            r = client2.post('/chal/{}'.format(chal2_id), data=data)

        # user2 is now on top
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user2'

        # user1 solves chal2
        with client1.session_transaction() as sess:
            data = {
                "key": 'flag',
                "nonce": sess.get('nonce')
            }
            r = client1.post('/chal/{}'.format(chal2_id), data=data)

        # user should still be on top because they solved chal2 first
        scores = get_scores(admin)
        assert scores[0]['team'] == 'user2'


def test_user_score_is_correct():
    '''Test that a user's score is correct'''
    app = create_ctfd()
    with app.app_context():
        # create user1
        register_user(app, name="user1", email="user1@ctfd.io")

        # create challenge
        chal = gen_challenge(app.db, value=100)
        flag = gen_flag(app.db, chal=chal.id, flag='flag')
        chal_id = chal.id

        # create a solve for the challenge for user1. (the id is 2 because of the admin)
        gen_solve(app.db, 2, chal_id)
        user1 = Teams.query.filter_by(id=2).first()

        # assert that user1's score is 100
        assert user1.score() == 100
        assert user1.place() == '1st'

        # create user2
        register_user(app, name="user2", email="user2@ctfd.io")

        # user2 solves the challenge
        gen_solve(app.db, 3, chal_id)

        # assert that user2's score is 100 but is in 2nd place
        user2 = Teams.query.filter_by(id=3).first()
        assert user2.score() == 100
        assert user2.place() == '2nd'

        # create an award for user2
        gen_award(app.db, 3, value=5)

        # assert that user2's score is now 105 and is in 1st place
        assert user2.score() == 105
        assert user2.place() == '1st'


def test_pages_routing_and_rendering():
    """Test that pages are routing and rendering"""
    app = create_ctfd()
    with app.app_context():
        html = '''##The quick brown fox jumped over the lazy dog'''
        route = 'test'
        page = gen_page(app.db, route, html)

        with app.test_client() as client:
            r = client.get('/test')
            output = r.get_data(as_text=True)
            assert "<h2>The quick brown fox jumped over the lazy dog</h2>" in output
    destroy_ctfd(app)


def test_themes_handler():
    """Test that the themes handler is working properly"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/themes/original/static/css/style.css')
            assert r.status_code == 200
            r = client.get('/themes/original/static/css/404_NOT_FOUND')
            assert r.status_code == 404
            r = client.get('/themes/original/static/%2e%2e/%2e%2e/%2e%2e/utils.py')
            assert r.status_code == 404
            r = client.get('/themes/original/static/%2e%2e%2f%2e%2e%2f%2e%2e%2futils.py')
            assert r.status_code == 404
            r = client.get('/themes/original/static/..%2f..%2f..%2futils.py')
            assert r.status_code == 404
            r = client.get('/themes/original/static/../../../utils.py')
            assert r.status_code == 404
    destroy_ctfd(app)


def test_ctfd_setup_redirect():
    """Test that a fresh CTFd instance redirects to /setup"""
    app = create_ctfd(setup=False)
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/teams')
            assert r.status_code == 302
            assert r.location == "http://localhost/setup"

            # Files in /themes load properly
            r = client.get('/themes/original/static/css/style.css')
            assert r.status_code == 200
    destroy_ctfd(app)


def test_user_cannot_unlock_hint():
    """Test that a user can't unlock a hint if they don't have enough points"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            register_user(app, name="user1", email="user1@ctfd.io")

            chal = gen_challenge(app.db, value=100)
            chal_id = chal.id

            flag = gen_flag(app.db, chal=chal.id, flag='flag')

            hint = gen_hint(db, chal_id, cost=10)
            hint_id = hint.id

            client = login_as_user(app, name="user1", password="password")

            with client.session_transaction() as sess:
                data = {
                    "nonce": sess.get('nonce')
                }
                r = client.post('/hints/{}'.format(hint_id), data=data)
                resp = json.loads(r.data.decode('utf8'))
                assert resp.get('errors') == 'Not enough points'
    destroy_ctfd(app)


def test_user_can_unlock_hint():
    """Test that a user can unlock a hint if they have enough points"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            register_user(app, name="user1", email="user1@ctfd.io")

            chal = gen_challenge(app.db, value=100)
            chal_id = chal.id

            flag = gen_flag(app.db, chal=chal.id, flag='flag')

            hint = gen_hint(app.db, chal_id, cost=10)
            hint_id = hint.id

            award = gen_award(app.db, teamid=2, value=15)

            client = login_as_user(app, name="user1", password="password")

            with client.session_transaction() as sess:
                data = {
                    "nonce": sess.get('nonce')
                }
                r = client.post('/hints/{}'.format(hint_id), data=data)
                resp = json.loads(r.data.decode('utf8'))
                assert resp.get('errors') is None
                assert resp.get('hint')
                assert resp.get('chal') == chal_id
    destroy_ctfd(app)


@patch('smtplib.SMTP')
@freeze_time("2012-01-14 03:21:34")
def test_user_can_confirm_email(mock_smtp):
    '''Test that a user is capable of confirming their email address'''
    app = create_ctfd()
    with app.app_context():
        # Set CTFd to only allow confirmed users and send emails
        set_config('verify_emails', True)
        set_config('mail_server', 'localhost')
        set_config('mail_port', 25)
        set_config('mail_username', 'username')
        set_config('mail_password', 'password')

        register_user(app, name="user1", email="user@user.com")

        # Teams are not verified by default
        team = Teams.query.filter_by(email='user@user.com').first()
        assert team.verified == False

        client = login_as_user(app, name="user1", password="password")

        # smtp.sendmail was called
        mock_smtp.return_value.sendmail.assert_called()

        with client.session_transaction() as sess:
            data = {
                "nonce": sess.get('nonce')
            }
            r = client.get('/challenges')
            assert r.location == "http://localhost/confirm"  # We got redirected to /confirm

            # Use precalculated confirmation secret
            r = client.get('http://localhost/confirm/InVzZXJAdXNlci5jb20iLkFmS0dQZy5kLUJnVkgwaUhadzFHaXVENHczWTJCVVJwdWc%3D')
            assert r.location == 'http://localhost/challenges'

            # The team is now verified
            team = Teams.query.filter_by(email='user@user.com').first()
            assert team.verified == True


@patch('smtplib.SMTP')
@freeze_time("2012-01-14 03:21:34")
def test_user_can_reset_password(mock_smtp):
    '''Test that a user is capable of resetting their password'''
    from email.mime.text import MIMEText
    app = create_ctfd()
    with app.app_context():
        # Set CTFd to send emails
        set_config('mail_server', 'localhost')
        set_config('mail_port', 25)
        set_config('mail_username', 'username')
        set_config('mail_password', 'password')

        # Create a user
        register_user(app, name="user1", email="user@user.com")

        with app.test_client() as client:
            r = client.get('/reset_password')

            # Build reset password data
            with client.session_transaction() as sess:
                data = {
                    'nonce': sess.get('nonce'),
                    'email': 'user@user.com'
                }

            # Issue the password reset request
            r = client.post('/reset_password', data=data)

            from_addr = get_config('mailfrom_addr') or app.config.get('MAILFROM_ADDR')
            to_addr = 'user@user.com'

            # Build the email
            msg = """
Did you initiate a password reset?

http://localhost/reset_password/InVzZXIxIi5BZktHUGcuTVhkTmZtOWU2U2xwSXZ1MlFwTjdwa3F5V3hR

"""
            email_msg = MIMEText(msg)
            email_msg['Subject'] = "Message from CTFd"
            email_msg['From'] = from_addr
            email_msg['To'] = to_addr

            # Make sure that the reset password email is sent
            mock_smtp.return_value.sendmail.assert_called_with(from_addr, [to_addr], email_msg.as_string())

            # Get user's original password
            team = Teams.query.filter_by(email="user@user.com").first()
            team_password_saved = team.password

            # Build the POST data
            with client.session_transaction() as sess:
                data = {
                    'nonce': sess.get('nonce'),
                    'password': 'passwordtwo'
                }

            # Do the password reset
            r = client.get('/reset_password')
            r = client.post('/reset_password/InVzZXIxIi5BZktHUGcuTVhkTmZtOWU2U2xwSXZ1MlFwTjdwa3F5V3hR', data=data)

            # Make sure that the user's password changed
            team = Teams.query.filter_by(email="user@user.com").first()
            assert team.password != team_password_saved
