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
        "//%09/example.com",
        "//\t/example.com",
    )
    app = create_ctfd()
    with app.test_request_context("/", base_url="http://examplectf.com"):
        for bad_url in bad_urls:
            assert is_safe_url(bad_url) is False, (
                f"Expected {bad_url!r} to be rejected as unsafe"
            )
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
            assert is_safe_url(good_url) is True, (
                f"Expected {good_url!r} to be accepted as safe"
            )
    destroy_ctfd(app)


def test_is_safe_url_open_redirect_payloads():
    """Test is_safe_url against open redirect bypass payload patterns.

    Covers percent-encoding tricks, Unicode abuses, userinfo injection, scheme
    confusion, and control-character obfuscation from common open-redirect
    payload lists.
    """
    # Payloads that must be blocked — any True return here is a vulnerability.
    bad_urls = (
        # --- userinfo / @ injection ---
        "//;@examplectf.com@google.com/",
        "//3H6k7lIAiqjfNeN@examplectf.com@google.com/",
        "//3H6k7lIAiqjfNeN@examplectf.com+@google.com/",
        "//examplectf.com:80?@google.com/",
        "//examplectf.com:80#@google.com/",
        "//google.com:80@examplectf.com/",
        "http://examplectf.com:80%40google.com/",
        "http://examplectf.com+&@google.com#+@examplectf.com/",
        # --- protocol-relative with extra slashes ---
        "//google.com",
        "////google.com",
        "////google.com/",
        "///google.com",
        # --- backslash as slash (Chrome behaviour) ---
        r"//\google.com",
        r"\/\/google.com/",
        r"/\/google.com",
        r"/\/google.com/",
        # --- scheme-relative with tab/newline smuggling (raw chars) ---
        "//\t/google.com",
        "//\n/google.com",
        # --- percent-encoded tab in authority ---
        "//%09/google.com",
        "///%09/google.com",
        # --- javascript: in various disguises ---
        "javascript:alert(1)",
        "javascript:alert(1);",
        "javascript://https://examplectf.com/?z=%0Aalert(1);//",
        "//%5cjavascript:alert(1)",
        # --- data: URIs ---
        "data:text/html;base64,PHNjcmlwdD5hbGVydCgiWFNTIik7PC9zY3JpcHQ+Cg==",
        "data:text/html,<script>alert(1)</script>",
        # --- absolute external URLs ---
        "http://google.com",
        "https://google.com",
        "https://google.com/",
        "https://google.com//",
        # --- RTL override in netloc (Unicode Cf category embedded) ---
        "//google‮.com",  # RIGHT-TO-LEFT OVERRIDE in hostname
        "//examplectf.com​@google.com",  # zero-width space before @
        # --- numeric/alternate IP representations ---
        "http://3627734734",  # decimal IP for 216.58.214.206
        "http://0xd83ad6ce",  # hex IP
        "http://0330.072.0326.0316",  # octal IP
        "http://216.58.214.206",
        # --- protocol-relative with percent-encoded backslash ---
        "//%5cgoogle.com",
        "///%5cgoogle.com",
        "////%5cgoogle.com",
        # --- https: absolute bypasses ---
        "https://google.com/%2e%2e",
        "https://google.com/%2f..",
        "https://examplectf.com@google.com/",
        "https://examplectf.com;@google.com",
        # --- fragment/query tricks that hide the real host ---
        "//google.com#@examplectf.com/",
        "https://google.com#examplectf.com",
        "https://google.com?examplectf.com",
        # --- soft-hyphen and other Unicode Cf chars at position 0 ---
        "\xadjavascript:alert(1)",  # U+00AD SOFT HYPHEN (category Cf)
        "​javascript:alert(1)",  # U+200B ZERO WIDTH SPACE (category Cf)
    )

    # Payloads that must be accepted — these are legitimate relative or
    # same-host URLs and a False return here breaks real navigation.
    good_urls = (
        # Percent-encoded paths that are genuinely relative (not external).
        # NOTE: %2f encodes '/', but Python's urlsplit + urljoin treat
        # '%2fgoogle.com' as a relative path segment, NOT as '/google.com',
        # so these safely resolve to examplectf.com/<encoded-path>.
        "%2fgoogle.com",
        "%2f%2fgoogle.com",  # encodes '//', but still parsed as a path
        # Fully percent-encoded 'http://google.com' — treated as opaque path.
        "%68%74%74%70%3a%2f%2f%67%6f%6f%67%6c%65%2e%63%6f%6d",
        # Angle brackets at start are invalid scheme chars; browser keeps on-host.
        "<>//google.com",
        "/<>//google.com",
        # CJK repeat mark is not a control character; resolves as path.
        "/〱google.com",  # U+3031 VERTICAL KANA REPEAT MARK
        # Percent-encoded tab before a javascript: path — stays relative.
        "%09/javascript:alert(1)",
        # SOH before an absolute URL — %01 is not a raw control char so
        # is_safe_url passes it; the browser parses %01https as a relative path.
        "%01https://google.com",
    )

    app = create_ctfd()
    with app.test_request_context("/", base_url="http://examplectf.com"):
        for url in bad_urls:
            assert is_safe_url(url) is False, (
                f"Expected {url!r} to be rejected as unsafe"
            )
        for url in good_urls:
            assert is_safe_url(url) is True, f"Expected {url!r} to be accepted as safe"
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
