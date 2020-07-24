from unittest.mock import Mock, patch

import requests

from CTFd.utils import get_config, set_config
from CTFd.utils.updates import update_check
from tests.helpers import create_ctfd, destroy_ctfd, login_as_user


def test_update_check_is_called():
    """Update checks happen on start"""
    app = create_ctfd()
    with app.app_context():
        assert get_config("version_latest") is None


@patch.object(requests, "get")
def test_update_check_identifies_update(fake_get_request):
    """Update checks properly identify new versions"""
    app = create_ctfd()
    with app.app_context():
        app.config["UPDATE_CHECK"] = True
        fake_response = Mock()
        fake_get_request.return_value = fake_response
        fake_response.json = lambda: {
            "resource": {
                "download_url": "https://api.github.com/repos/CTFd/CTFd/zipball/9.9.9",
                "html_url": "https://github.com/CTFd/CTFd/releases/tag/9.9.9",
                "id": 12,
                "latest": True,
                "next": 1542212248,
                "prerelease": False,
                "published_at": "Wed, 25 Oct 2017 19:39:42 -0000",
                "tag": "9.9.9",
            }
        }
        update_check()
        assert (
            get_config("version_latest")
            == "https://github.com/CTFd/CTFd/releases/tag/9.9.9"
        )
        assert get_config("next_update_check") == 1542212248
    destroy_ctfd(app)


def test_update_check_notifies_user():
    """If an update is available, admin users are notified in the panel"""
    app = create_ctfd()
    with app.app_context():
        app.config["UPDATE_CHECK"] = True
        set_config("version_latest", "https://github.com/CTFd/CTFd/releases/tag/9.9.9")
        client = login_as_user(app, name="admin", password="password")

        r = client.get("/admin/config")
        assert r.status_code == 200

        response = r.get_data(as_text=True)
        assert "https://github.com/CTFd/CTFd/releases/tag/9.9.9" in response

    destroy_ctfd(app)


@patch.object(requests, "post")
def test_update_check_ignores_downgrades(fake_post_request):
    """Update checks do nothing on old or same versions"""
    app = create_ctfd()
    with app.app_context():
        app.config["UPDATE_CHECK"] = True
        fake_response = Mock()
        fake_post_request.return_value = fake_response
        fake_response.json = lambda: {
            u"resource": {
                u"html_url": u"https://github.com/CTFd/CTFd/releases/tag/0.0.1",
                u"download_url": u"https://api.github.com/repos/CTFd/CTFd/zipball/0.0.1",
                u"published_at": u"Wed, 25 Oct 2017 19:39:42 -0000",
                u"tag": u"0.0.1",
                u"prerelease": False,
                u"id": 6,
                u"latest": True,
            }
        }
        update_check()
        assert get_config("version_latest") is None

        fake_response = Mock()
        fake_post_request.return_value = fake_response
        fake_response.json = lambda: {
            u"resource": {
                u"html_url": u"https://github.com/CTFd/CTFd/releases/tag/{}".format(
                    app.VERSION
                ),
                u"download_url": u"https://api.github.com/repos/CTFd/CTFd/zipball/{}".format(
                    app.VERSION
                ),
                u"published_at": u"Wed, 25 Oct 2017 19:39:42 -0000",
                u"tag": u"{}".format(app.VERSION),
                u"prerelease": False,
                u"id": 6,
                u"latest": True,
            }
        }
        update_check()
        assert get_config("version_latest") is None
    destroy_ctfd(app)
