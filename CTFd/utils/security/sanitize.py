from lxml.html import html5parser, tostring
from lxml.html.clean import Cleaner
from lxml.html.defs import safe_attrs

cleaner = Cleaner(
    page_structure=False,
    embedded=False,
    frames=False,
    forms=False,
    links=False,
    meta=False,
    style=False,
    safe_attrs=(safe_attrs | set(["style"])),
    annoying_tags=False,
)


def sanitize_html(html):
    html = html5parser.fragment_fromstring(html, create_parent="div")
    html = cleaner.clean_html(tostring(html)).decode()
    return html
