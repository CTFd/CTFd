from CTFd.utils import set_config
from flask import url_for
from tests.helpers import (
    create_ctfd,
    destroy_ctfd,
    gen_challenge,
    gen_solve,
    login_as_user,
    register_user,
)
import re


def test_share_endpoints():
    """Test that social share endpoints and disabling are working"""
    app = create_ctfd(ctf_theme="core-beta")
    with app.app_context():
        chal_id = gen_challenge(app.db).id
        register_user(app)
        gen_solve(app.db, user_id=2, challenge_id=chal_id)

        # Test disabled shares dont work
        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/shares",
                json={"type": "solve", "user_id": 2, "challenge_id": 1},
            )
            assert r.status_code == 403

        set_config("social_shares", True)

        # Test working share
        with login_as_user(app) as client:
            r = client.post(
                "/api/v1/shares",
                json={"type": "solve", "user_id": 2, "challenge_id": 1},
            )
            resp = r.get_json()
            url = resp["data"]["url"]

        # Test loadding share page
        with app.test_client() as client:
            r = client.get(url)
            resp = r.get_data(as_text=True)
            assert r.status_code == 200
            assert "user has solved" in resp
            assert "chal_name has 1 solve" in resp

            # Test downloading asset image
            m = re.search(r'og:image(.*)', resp)
            # Remove extra text
            asset_url = m.group()[19:-4].replace("&amp;", "&")
            r = client.get(asset_url)
            assert r.status_code == 200

        # Test disabled social shares
        set_config("social_shares", False)
        with app.test_client() as client:
            r = client.get(url)
            assert r.status_code == 403
    destroy_ctfd(app)
