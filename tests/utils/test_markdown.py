from CTFd.utils import markdown


def test_markdown():
    """
    Test that our markdown function renders properly
    """
    # Allow raw HTML / potentially unsafe HTML
    assert (
        markdown("<iframe src='https://example.com'></iframe>").strip()
        == "<iframe src='https://example.com'></iframe>"
    )
