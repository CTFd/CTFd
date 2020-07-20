# Bandit complains about security issues with lxml.
# These issues have been addressed in the past and do not apply to parsing HTML.
from lxml.html import html5parser, tostring  # nosec B410
from lxml.html.clean import Cleaner  # nosec B410
from lxml.html.defs import safe_attrs  # nosec B410

cleaner = Cleaner(
    comments=False,
    page_structure=False,
    embedded=False,
    frames=False,
    forms=False,
    links=False,
    meta=False,
    style=False,
    safe_attrs=(
        safe_attrs
        | set(
            [
                "style",
                # Allow data attributes from bootstrap elements
                "data-toggle",
                "data-target",
                "data-dismiss",
                "data-spy",
                "data-offset",
                "data-html",
                "data-placement",
                "data-parent",
                "data-title",
                "data-template",
                "data-interval",
                "data-keyboard",
                "data-pause",
                "data-ride",
                "data-wrap",
                "data-touch",
                "data-flip",
                "data-boundary",
                "data-reference",
                "data-display",
                "data-animation",
                "data-container",
                "data-delay",
                "data-selector",
                "data-content",
                "data-trigger",
            ]
        )
    ),
    annoying_tags=False,
)


def sanitize_html(html):
    html = html5parser.fragment_fromstring(html, create_parent="div")
    html = cleaner.clean_html(tostring(html)).decode()
    return html
