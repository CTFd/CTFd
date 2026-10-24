import configparser
import runpy
from unittest.mock import Mock, patch

import pytest

import CTFd.config
from CTFd.utils.email.providers.mailgun import MailgunEmailProvider
from tests.helpers import create_ctfd, destroy_ctfd


@pytest.mark.parametrize("source", ["ini", "environment"])
def test_mailgun_base_url_is_independent_of_api_key(monkeypatch, source):
    base_url = "https://api.eu.mailgun.net/v3/example.test"
    api_key = "synthetic-mailgun-key-for-tests"
    original_read = configparser.ConfigParser.read

    def read(parser, *args, **kwargs):
        result = original_read(parser, *args, **kwargs)
        parser.set("email", "MAILGUN_BASE_URL", base_url if source == "ini" else "")
        parser.set("email", "MAILGUN_API_KEY", api_key if source == "ini" else "")
        return result

    monkeypatch.setenv("MAILGUN_BASE_URL", base_url)
    monkeypatch.setenv("MAILGUN_API_KEY", api_key)
    with monkeypatch.context() as context:
        context.setattr(configparser.ConfigParser, "read", read)
        config = runpy.run_path(CTFd.config.__file__)["Config"]

    assert config.MAILGUN_BASE_URL == base_url
    assert config.MAILGUN_API_KEY == api_key

    app = create_ctfd()
    with app.app_context():
        app.config["MAILGUN_BASE_URL"] = config.MAILGUN_BASE_URL
        app.config["MAILGUN_API_KEY"] = config.MAILGUN_API_KEY
        with patch(
            "CTFd.utils.email.providers.mailgun.requests.post",
            return_value=Mock(status_code=200),
        ) as post:
            assert MailgunEmailProvider.sendmail(
                "player@example.test", "Test message", "Test subject"
            ) == (True, "Email sent")
        assert post.call_args.args[0] == base_url + "/messages"
        assert post.call_args.kwargs["auth"] == ("api", api_key)
    destroy_ctfd(app)
