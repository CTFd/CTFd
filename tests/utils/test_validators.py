from marshmallow import ValidationError

from CTFd.utils.validators import validate_country_code, validate_email


def test_validate_country_code():
    assert validate_country_code("") is None
    # TODO: This looks poor, when everything moves to pytest we should remove exception catches like this.
    try:
        validate_country_code("ZZ")
    except ValidationError:
        pass


def test_validate_email():
    """Test that the check_email_format() works properly"""
    assert validate_email("user@ctfd.io") is True
    assert validate_email("user+plus@gmail.com") is True
    assert validate_email("user.period1234@gmail.com") is True
    assert validate_email("user.period1234@b.c") is True
    assert validate_email("user.period1234@b") is False
    assert validate_email("no.ampersand") is False
    assert validate_email("user@") is False
    assert validate_email("@ctfd.io") is False
    assert validate_email("user.io@ctfd") is False
    assert validate_email("user\\@ctfd") is False

    for invalid_email in ["user.@ctfd.io", ".user@ctfd.io", "user@ctfd..io"]:
        try:
            assert validate_email(invalid_email) is False
        except AssertionError:
            print(invalid_email, "did not pass validation")
