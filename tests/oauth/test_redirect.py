#!/usr/bin/env python
# -*- coding: utf-8 -*-

from tests.helpers import *
from mock import Mock, patch
from CTFd.utils import set_config
import requests


def test_oauth_not_configured():
    """Test that OAuth redirection fails if OAuth settings aren't configured"""
    app = create_ctfd()
    with app.app_context():
        with app.test_client() as client:
            r = client.get('/oauth', follow_redirects=False)
            assert r.location == 'http://localhost/login'
            r = client.get(r.location)
            resp = r.get_data(as_text=True)
            assert "OAuth Settings not configured" in resp
    destroy_ctfd(app)


@patch.object(requests, 'get')
@patch.object(requests, 'post')
def test_oauth_configured_flow(fake_post_request, fake_get_request):
    app = create_ctfd(user_mode="teams")
    app.config.update({
        'OAUTH_CLIENT_ID': 'ctfd_testing_client_id',
        'OAUTH_CLIENT_SECRET': 'ctfd_testing_client_secret',
        'OAUTH_AUTHORIZATION_ENDPOINT': 'http://auth.localhost/oauth/authorize',
        'OAUTH_TOKEN_ENDPOINT': 'http://auth.localhost/oauth/token',
        'OAUTH_API_ENDPOINT': 'http://api.localhost/user',
    })
    with app.app_context():
        set_config('registration_visibility', 'private')
        assert Users.query.count() == 1
        assert Teams.query.count() == 0
        with app.test_client() as client:
            client.get('/login')
            with client.session_transaction() as sess:
                nonce = sess['nonce']

                redirect_url = "{endpoint}?response_type=code&client_id={client_id}&scope={scope}&state={state}".format(
                    endpoint=app.config['OAUTH_AUTHORIZATION_ENDPOINT'],
                    client_id=app.config['OAUTH_CLIENT_ID'],
                    scope='profile%20team',
                    state=nonce
                )

            r = client.get('/oauth', follow_redirects=False)
            assert r.location == redirect_url

            fake_post_response = Mock()
            fake_post_request.return_value = fake_post_response
            fake_post_response.status_code = 200
            fake_post_response.json = lambda: {
                'access_token': 'fake_mlc_access_token'
            }

            fake_get_response = Mock()
            fake_get_request.return_value = fake_get_response
            fake_post_response.status_code = 200
            fake_get_response.json = lambda: {
                'id': 1337,
                'name': 'user',
                'email': 'user@ctfd.io',
                'team': {
                    'id': 1234,
                    'name': 'TestTeamTen'
                }
            }

            r = client.get('/redirect?code={code}&state={state}'.format(
                code='mlc_test_code',
                state=nonce
            ))

            assert Users.query.count() == 1
            assert r.location == 'http://localhost/login'

            resp = client.get(r.location).get_data(as_text=True)
            assert 'Public registration is disabled' in resp

            set_config('registration_visibility', 'public')

            r = client.get('/redirect?code={code}&state={state}'.format(
                code='mlc_test_code',
                state=nonce
            ))

            assert Users.query.count() == 2
            user = Users.query.filter_by(email='user@ctfd.io').first()
            assert user.oauth_id == 1337
            assert user.team_id == 1
            assert Teams.query.count() == 1
            team = Teams.query.filter_by(id=1).first()
            assert team.oauth_id == 1234
    destroy_ctfd(app)
