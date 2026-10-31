import configparser
import runpy

import pytest

import CTFd.config


def load_partial_config(monkeypatch, contents):
    def read(parser, *args, **kwargs):
        parser.read_string(contents)
        return []

    monkeypatch.setattr(configparser.ConfigParser, "read", read)
    monkeypatch.setenv("SECRET_KEY", "partial-config-test")
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    return runpy.run_path(CTFd.config.__file__)["Config"]


@pytest.mark.parametrize("contents", ["", "[server]\n", "[server]\nDATABASE_URL =\n"])
def test_partial_ini_retains_defaults_and_environment(monkeypatch, contents):
    monkeypatch.setenv("MAIL_PORT", "2525")
    monkeypatch.setenv("MAIL_USEAUTH", "true")
    monkeypatch.setenv("APPLICATION_ROOT", "/competition")
    monkeypatch.setenv("SESSION_COOKIE_HTTPONLY", "false")
    monkeypatch.setenv("PERMANENT_SESSION_LIFETIME", "3600")
    config = load_partial_config(monkeypatch, contents)

    assert config.SECRET_KEY == "partial-config-test"
    assert config.SQLALCHEMY_DATABASE_URI == "sqlite://"
    assert config.MAIL_PORT == 2525
    assert config.MAIL_USEAUTH is True
    assert config.APPLICATION_ROOT == "/competition"
    assert config.SESSION_COOKIE_HTTPONLY is False
    assert config.PERMANENT_SESSION_LIFETIME == 3600
    assert config.SESSION_COOKIE_SAMESITE == "Lax"
    assert config.MAILFROM_ADDR == "noreply@examplectf.com"


def test_partial_ini_explicit_values_win_and_extra_options_stay_local(monkeypatch):
    monkeypatch.setenv("MAIL_SERVER", "environment.example")
    monkeypatch.setenv("UNRELATED_CONFIG_VALUE", "not-an-extra-option")
    config = load_partial_config(
        monkeypatch,
        "[email]\nMAIL_SERVER = ini.example\n[extra]\nCUSTOM_OPTION = configured\n",
    )

    assert config.MAIL_SERVER == "ini.example"
    assert config.CUSTOM_OPTION == "configured"
    assert not hasattr(config, "UNRELATED_CONFIG_VALUE")


def test_partial_ini_rejects_invalid_typed_environment_value(monkeypatch):
    monkeypatch.setenv("PERMANENT_SESSION_LIFETIME", "not-an-integer")
    with pytest.raises(ValueError):
        load_partial_config(monkeypatch, "")


def test_partial_ini_still_rejects_builtins_in_extra(monkeypatch):
    with pytest.raises(ValueError, match="Built-in Config SECRET_KEY"):
        load_partial_config(monkeypatch, "[extra]\nSECRET_KEY = duplicate\n")


def test_partial_ini_empty_typed_environment_uses_defaults(monkeypatch):
    monkeypatch.setenv("PERMANENT_SESSION_LIFETIME", "")
    monkeypatch.setenv("SESSION_COOKIE_HTTPONLY", "")
    config = load_partial_config(monkeypatch, "")
    assert config.PERMANENT_SESSION_LIFETIME == 604800
    assert config.SESSION_COOKIE_HTTPONLY is True
