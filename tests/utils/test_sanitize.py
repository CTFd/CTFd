from collections import namedtuple

from CTFd.utils.security.sanitize import sanitize_html

Case = namedtuple("Case", ["input", "expected"])


def test_sanitize_html_empty():
    """Test sanitize_html with empty input"""
    assert sanitize_html("") == ""


def test_sanitize_html_basic_tags():
    """Test that basic HTML tags are preserved"""
    cases = [
        Case("<p>Hello World</p>", "<p>Hello World</p>"),
        Case("<div>Content</div>", "<div>Content</div>"),
        Case("<span>Text</span>", "<span>Text</span>"),
        Case("<strong>Bold</strong>", "<strong>Bold</strong>"),
        Case("<em>Italic</em>", "<em>Italic</em>"),
        Case("<h1>Header</h1>", "<h1>Header</h1>"),
        Case("<h2>Header</h2>", "<h2>Header</h2>"),
        Case("<h3>Header</h3>", "<h3>Header</h3>"),
        Case(
            "<ul><li>Item 1</li><li>Item 2</li></ul>",
            "<ul><li>Item 1</li><li>Item 2</li></ul>",
        ),
        Case(
            "<ol><li>Item 1</li><li>Item 2</li></ol>",
            "<ol><li>Item 1</li><li>Item 2</li></ol>",
        ),
    ]

    for case in cases:
        assert sanitize_html(case.input) == case.expected


def test_sanitize_html_links():
    """Test that links are sanitized with proper rel attributes"""
    cases = [
        Case(
            '<a href="https://example.com">Link</a>',
            '<a href="https://example.com" rel="noopener noreferrer nofollow">Link</a>',
        ),
        Case(
            '<a href="http://example.com">Link</a>',
            '<a href="http://example.com" rel="noopener noreferrer nofollow">Link</a>',
        ),
        Case(
            '<a href="//example.com">Link</a>',
            '<a href="//example.com" rel="noopener noreferrer nofollow">Link</a>',
        ),
        Case(
            '<a href="/internal/path">Link</a>',
            '<a href="/internal/path" rel="noopener noreferrer nofollow">Link</a>',
        ),
        Case(
            '<a href="mailto:test@example.com">Email</a>',
            '<a href="mailto:test@example.com" rel="noopener noreferrer nofollow">Email</a>',
        ),
        Case(
            '<a href="tel:+1234567890">Phone</a>',
            '<a href="tel:+1234567890" rel="noopener noreferrer nofollow">Phone</a>',
        ),
        Case(
            '<a href="javascript:alert(1)">Evil</a>',
            '<a rel="noopener noreferrer nofollow">Evil</a>',
        ),
        Case(
            '<a href="#anchor">Anchor</a>',
            '<a href="#anchor" rel="noopener noreferrer nofollow">Anchor</a>',
        ),
        Case(
            '<a href="?q=1">Query</a>',
            '<a href="?q=1" rel="noopener noreferrer nofollow">Query</a>',
        ),
        Case(
            '<a href="?q=1&r=2">Query</a>',
            '<a href="?q=1&amp;r=2" rel="noopener noreferrer nofollow">Query</a>',
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_images():
    """Test that images are preserved with allowed attributes"""
    cases = [
        Case(
            '<img src="https://example.com/image.jpg" alt="Test Image">',
            '<img src="https://example.com/image.jpg" alt="Test Image">',
        ),
        Case(
            '<img src="image.jpg" alt="Local Image" width="100" height="100">',
            '<img src="image.jpg" alt="Local Image" width="100" height="100">',
        ),
        Case(
            '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot">',
            '<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUAAAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO9TXL0Y4OHwAAAABJRU5ErkJggg==" alt="Red dot">',
        ),
        Case(
            '<img src="image.gif?height=500&width=500" alt="Animated">',
            '<img src="image.gif?height=500&amp;width=500" alt="Animated">',
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_dangerous_content():
    """Test that dangerous content is removed or sanitized"""
    cases = [
        Case('<script>alert("xss")</script>', ""),
        Case('<script src="evil.js"></script>', ""),
        Case('<object data="evil.swf"></object>', ""),
        Case('<embed src="evil.swf">', ""),
        Case('<link rel="stylesheet" href="evil.css">', ""),
        Case("<div onclick=\"alert('xss')\">Content</div>", "<div>Content</div>"),
        Case('<img src="image.jpg" onload="alert(\'xss\')">', '<img src="image.jpg">'),
        Case('<img src="image.jpg" onerror="alert(\'xss\')">', '<img src="image.jpg">'),
        Case("<body onload=\"alert('xss')\">Content</body>", "Content"),
        Case('<iframe src="javascript:alert(1)"></iframe>', "<iframe></iframe>"),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_forms():
    """Test that form elements are preserved"""
    cases = [
        Case(
            '<form method="post" action="/submit"><input type="text" name="username"></form>',
            '<form method="post" action="/submit"><input type="text" name="username"></form>',
        ),
        Case(
            '<textarea name="message" placeholder="Enter message"></textarea>',
            '<textarea name="message" placeholder="Enter message"></textarea>',
        ),
        Case(
            '<select name="option"><option value="1">Option 1</option></select>',
            '<select name="option"><option value="1">Option 1</option></select>',
        ),
        Case(
            '<button type="submit">Submit</button>',
            '<button type="submit">Submit</button>',
        ),
        Case(
            '<label for="username">Username:</label>',
            '<label for="username">Username:</label>',
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_media():
    """Test that media elements are preserved"""
    cases = [
        Case(
            '<video controls src="video.mp4" width="640" height="480"></video>',
            '<video controls="" src="video.mp4" width="640" height="480"></video>',
        ),
        Case(
            '<audio controls src="audio.mp3"></audio>',
            '<audio controls="" src="audio.mp3"></audio>',
        ),
        Case(
            '<iframe src="https://example.com" width="600" height="400" frameborder="0"></iframe>',
            '<iframe src="https://example.com" width="600" height="400" frameborder="0"></iframe>',
        ),
        Case(
            '<source src="video.mp4" type="video/mp4">',
            '<source src="video.mp4" type="video/mp4">',
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        print(result)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_tables():
    """Test that table elements are preserved"""
    cases = [
        Case(
            "<table><tr><th>Header</th><td>Data</td></tr></table>",
            "<table><tbody><tr><th>Header</th><td>Data</td></tr></tbody></table>",
        ),
        Case(
            '<table border="1" cellpadding="5" cellspacing="0"><tbody><tr><td>Cell</td></tr></tbody></table>',
            '<table border="1" cellpadding="5" cellspacing="0"><tbody><tr><td>Cell</td></tr></tbody></table>',
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_attributes():
    """Test that allowed attributes are preserved and dangerous ones removed"""
    cases = [
        Case(
            '<div class="container" id="main" style="color: red;">Content</div>',
            '<div class="container" id="main" style="color: red;">Content</div>',
        ),
        Case(
            '<div data-toggle="modal" data-target="#myModal">Modal</div>',
            '<div data-toggle="modal" data-target="#myModal">Modal</div>',
        ),
        Case(
            '<button aria-label="Close" aria-expanded="false">Button</button>',
            '<button aria-label="Close" aria-expanded="false">Button</button>',
        ),
        Case(
            '<img src="image.jpg" title="Image Title" alt="Alt Text">',
            '<img src="image.jpg" title="Image Title" alt="Alt Text">',
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_comments():
    """Test that HTML comments are preserved"""
    cases = [
        Case(
            "<!-- This is a comment --><p>Content</p>",
            "<!-- This is a comment --><p>Content</p>",
        ),
        Case(
            "<div>Before<!-- comment -->After</div>",
            "<div>Before<!-- comment -->After</div>",
        ),
        Case(
            "<!--&gt;<img src=x onerror=alert()&gt;>",
            "<!--&gt;<img src=x onerror=alert()&gt;>-->",
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_href_sanitization():
    """Test that href attributes are properly sanitized"""
    cases = [
        Case(
            'abc<a href="https://abc&quot;&gt;<script&gt;alert(1)<&#x2f;script/">CLICK</a>',
            'abc<a rel="noopener noreferrer nofollow">CLICK</a>',
        ),
        Case(
            '<a href="https://abc&quot;&gt;<script&gt;alert(1)<&#x2f;script/">Link</a>',
            '<a rel="noopener noreferrer nofollow">Link</a>',
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_malformed():
    """Test sanitize_html with malformed HTML"""
    cases = [
        Case("<p>Unclosed paragraph", "<p>Unclosed paragraph</p>"),
        Case(
            "<strong><em>Improperly nested</strong></em>",
            "<strong><em>Improperly nested</em></strong>",
        ),
        Case("Text with & ampersand", "Text with &amp; ampersand"),
        Case("Text with < less than", "Text with &lt; less than"),
        Case("Text with > greater than", "Text with &gt; greater than"),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_whitespace():
    """Test that whitespace is preserved correctly"""
    cases = [
        Case("Hi.\n", "Hi.\n"),
        Case("\t\n \n\t", "\t\n \n\t"),
        Case("  <p>  Spaced content  </p>  ", "  <p>  Spaced content  </p>  "),
        Case("<pre>  Code with spaces  </pre>", "<pre>  Code with spaces  </pre>"),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"


def test_sanitize_html_complex_content():
    """Test sanitize_html with complex mixed content"""
    cases = [
        Case(
            """<div class="container">
    <h1>Welcome to CTF</h1>
    <p>This is a <strong>challenge description</strong> with <em>formatting</em>.</p>
    <ul>
        <li>Hint 1: Look at the source</li>
        <li>Hint 2: Check the headers</li>
    </ul>
    <p>Visit <a href="https://example.com">this link</a> for more info.</p>
    <img src="https://example.com/flag.png" alt="Flag" width="200">
    <!-- This is a comment -->
    <pre><code>print("Hello World")</code></pre>
</div>""",
            """<div class="container">
    <h1>Welcome to CTF</h1>
    <p>This is a <strong>challenge description</strong> with <em>formatting</em>.</p>
    <ul>
        <li>Hint 1: Look at the source</li>
        <li>Hint 2: Check the headers</li>
    </ul>
    <p>Visit <a href="https://example.com" rel="noopener noreferrer nofollow">this link</a> for more info.</p>
    <img src="https://example.com/flag.png" alt="Flag" width="200">
    <!-- This is a comment -->
    <pre><code>print("Hello World")</code></pre>
</div>""",
        ),
    ]

    for case in cases:
        result = sanitize_html(case.input)
        assert (
            result == case.expected
        ), f"Input: {case.input}, Expected: {case.expected}, Got: {result}"
