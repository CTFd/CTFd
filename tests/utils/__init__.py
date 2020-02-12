#!/usr/bin/env python
# -*- coding: utf-8 -*-

from CTFd.utils import get_config, set_config
from tests.helpers import create_ctfd, destroy_ctfd


def test_ctf_version_is_set():
    """Does ctf_version get set correctly"""
    app = create_ctfd()
    with app.app_context():
        assert get_config("ctf_version") == app.VERSION
    destroy_ctfd(app)


def test_get_config_and_set_config():
    """Does get_config and set_config work properly"""
    app = create_ctfd()
    with app.app_context():
        assert get_config("setup") == True
        config = set_config("TEST_CONFIG_ENTRY", "test_config_entry")
        assert config.value == "test_config_entry"
        assert get_config("TEST_CONFIG_ENTRY") == "test_config_entry"
    destroy_ctfd(app)
