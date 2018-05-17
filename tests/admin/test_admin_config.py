from tests.helpers import *
from CTFd.models import Teams, Challenges
from CTFd.utils import get_config, set_config, override_template, sendmail, verify_email, ctf_started, ctf_ended
from CTFd.plugins.challenges import get_chal_class
from freezegun import freeze_time
from mock import patch


def test_admin_post_config_values():
    """Test that admins can POST configuration values"""
    app = create_ctfd()
    with app.app_context():
        client = login_as_user(app, name="admin", password="password")

        with client.session_transaction() as sess:
            data = {
                'nonce': sess.get('nonce'),
                'ctf_name': 'CTFd',
                'ctf_logo': '',
                'ctf_theme': 'core',
                'workshop_mode': 'on',
                'paused': 'on',
                'hide_scores': 'on',
                'css': 'None',
                'verify_emails': 'on',
                'view_challenges_unregistered': 'on',
                'view_scoreboard_if_authed': 'on',
                'prevent_registration': 'on',
                'prevent_name_change': 'on',
                'mailfrom_addr': 'user@ctfd.io',
                'mail_server': 'mail.failmail.com',
                'mail_port': '587',
                'mail_useauth': 'on',
                'mail_u': 'username',
                'mail_p': 'password',
                'mail_tls': 'on',
                'mg_base_url': '',
                'mg_api_key': '',
                'start-month': '',
                'start-day': '',
                'start-year': '',
                'start-hour': '',
                'start-minute': '',
                'start': '',
                'end-month': '',
                'end-day': '',
                'end-year': '',
                'end-hour': '',
                'end-minute': '',
                'end': '',
                'freeze-month': '',
                'freeze-day': '',
                'freeze-year': '',
                'freeze-hour': '',
                'freeze-minute': '',
                'freeze': '',
                'backup': ''
            }
            r = client.post('/admin/config', data=data)

        result = {
            'ctf_name': 'CTFd',
            'ctf_logo': None,
            'ctf_theme': 'core',
            'workshop_mode': True,
            'paused': True,
            'hide_scores': True,
            'css': 'None',
            'verify_emails': True,
            'view_challenges_unregistered': True,
            'view_scoreboard_if_authed': True,
            'prevent_registration': True,
            'prevent_name_change': True,
            'mailfrom_addr': 'user@ctfd.io',
            'mail_server': 'mail.failmail.com',
            'mail_port': 587,
            'mail_useauth': True,
            'mail_username': 'username',
            'mail_password': 'password',
            'mail_tls': True,
            'mg_base_url': None,
            'mg_api_key': None,
            'start-month': None,
            'start-day': None,
            'start-year': None,
            'start-hour': None,
            'start-minute': None,
            'start': None,
            'end-month': None,
            'end-day': None,
            'end-year': None,
            'end-hour': None,
            'end-minute': None,
            'end': None,
            'freeze-month': None,
            'freeze-day': None,
            'freeze-year': None,
            'freeze-hour': None,
            'freeze-minute': None,
            'freeze': None,
            'backup': None
        }

        for key in result:
            if result[key]:
                assert get_config(key) == result[key]
            else:
                assert get_config(key) is None

    destroy_ctfd(app)
