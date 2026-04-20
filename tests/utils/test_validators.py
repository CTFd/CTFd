from marshmallow import ValidationError

from CTFd.utils.validators import is_safe_url, validate_country_code, validate_email
from tests.helpers import create_ctfd, destroy_ctfd


def test_is_safe_url_bad_urls():
    """Test that is_safe_url rejects malicious and external URLs (ported from Django's url_has_allowed_host_and_scheme tests)"""
    bad_urls = (
        "http://example.com",
        "http:///example.com",
        "https://example.com",
        "ftp://example.com",
        r"\\example.com",
        r"\\\example.com",
        r"/\\/example.com",
        r"\\\example.com",
        r"\\example.com",
        r"\\//example.com",
        r"/\/example.com",
        r"\/example.com",
        r"/\example.com",
        "http:///example.com",
        r"http:/\//example.com",
        r"http:\/example.com",
        r"http:/\example.com",
        'javascript:alert("XSS")',
        "java\r\nscript\r\n:alert(0)",
        "\njavascript:alert(x)",
        "java\nscript:alert(x)",
        "\x08//example.com",
        r"http://otherserver\@example.com",
        r"http:\\testserver\@example.com",
        r"http://testserver\me:pass@example.com",
        r"http://testserver\@example.com",
        r"http:\\testserver\confirm\me@example.com",
        "http:999999999",
        "ftp:9999999999",
        "\n",
        "http://[2001:cdba:0000:0000:0000:0000:3257:9652/",
        "http://2001:cdba:0000:0000:0000:0000:3257:9652]/",
        "////example.com",
        "\\\\example.com",
        "http:///example.com",
        "https:///example.com",
        "https:example.com",
        r"\/\/example.com/",
        r"/\/example.com/",
        "//example%E3%80%82com",
        "http://examplectf.com@example.com/",
        "http://www.example.com?http://examplectf.com/",
        "http://www.example.com?folder/www.folder.com",
        "https://evil.c℀.example.com",
    )
    app = create_ctfd()
    with app.test_request_context("/", base_url="http://examplectf.com"):
        for bad_url in bad_urls:
            assert (
                is_safe_url(bad_url) is False
            ), f"Expected {bad_url!r} to be rejected as unsafe"
    destroy_ctfd(app)


def test_is_safe_url_good_urls():
    """Test that is_safe_url accepts safe relative and same-host URLs (ported from Django's url_has_allowed_host_and_scheme tests)"""
    good_urls = (
        "/view/?param=http://example.com",
        "/view/?param=https://example.com",
        "/view?param=ftp://example.com",
        "view/?param=//example.com",
        "https://examplectf.com/",
        "HTTPS://examplectf.com/",
        "//examplectf.com/",
        "http://examplectf.com/confirm?email=me@example.com",
        "/url%20with%20spaces/",
        "path/http:2222222222",
    )
    app = create_ctfd()
    with app.test_request_context("/", base_url="http://examplectf.com"):
        for good_url in good_urls:
            assert (
                is_safe_url(good_url) is True
            ), f"Expected {good_url!r} to be accepted as safe"
    destroy_ctfd(app)


def test_validate_country_code():
    assert validate_country_code("") is None
    # TODO: This looks poor, when everything moves to pytest we should remove exception catches like this.
    try:
        validate_country_code("ZZ")
    except ValidationError:
        pass


def test_validate_email():
    """Test that the check_email_format() works properly"""
    assert validate_email("user@examplectf.com") is True
    assert validate_email("user+plus@gmail.com") is True
    assert validate_email("user.period1234@gmail.com") is True
    assert validate_email("user.period1234@b.c") is True
    assert validate_email("user.period1234@b") is False
    assert validate_email("no.ampersand") is False
    assert validate_email("user@") is False
    assert validate_email("@examplectf.com") is False
    assert validate_email("user.io@ctfd") is False
    assert validate_email("user\\@ctfd") is False

    for invalid_email in [
        "user.@examplectf.com",
        ".user@examplectf.com",
        "user@ctfd..io",
    ]:
        try:
            assert validate_email(invalid_email) is False
        except AssertionError:
            print(invalid_email, "did not pass validation")
