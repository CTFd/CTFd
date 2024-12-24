import nh3
from copy import deepcopy

HTML_ALLOWED_ATTRIBUTES = deepcopy(nh3.ALLOWED_ATTRIBUTES)


# Copied from lxml:
# https://github.com/lxml/lxml/blob/e986a9cb5d54827c59aefa8803bc90954d67221e/src/lxml/html/defs.py#L38
# We specifically remove rel to support the link_rel parameter
# fmt: off
SAFE_ATTRS = (
    'abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'align',
    'alt', 'axis', 'border', 'cellpadding', 'cellspacing', 'char', 'charoff',
    'charset', 'checked', 'cite', 'class', 'clear', 'cols', 'colspan',
    'color', 'compact', 'coords', 'datetime', 'dir', 'disabled', 'enctype',
    'for', 'frame', 'headers', 'height', 'href', 'hreflang', 'hspace', 'id',
    'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method',
    'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'readonly',
    'rev', 'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape',
    'size', 'span', 'src', 'start', 'summary', 'tabindex', 'target', 'title',
    'type', 'usemap', 'valign', 'value', 'vspace', 'width'
)
# fmt: on

PAGE_STRUCTURE_TAGS = {
    "title": [],
}

META_TAGS = {
    "meta": ["name", "content", "property"],
}

FORM_TAGS = {
    "form": ["method", "action"],
    "button": ["name", "type", "value", "disabled"],
    "input": ["name", "type", "value", "placeholder"],
    "select": ["name", "value", "placeholder"],
    "option": ["value"],
    "textarea": ["name", "value", "placeholder"],
    "label": ["for"],
}

ANNOYING_TAGS = {
    "blink": [],
    "marquee": [],
}


MEDIA_TAGS = {
    "audio": ["autoplay", "controls", "crossorigin", "loop", "muted", "preload", "src"],
    "video": [
        "autoplay",
        "buffered",
        "controls",
        "crossorigin",
        "loop",
        "muted",
        "playsinline",
        "poster",
        "preload",
        "src",
    ],
    "source": ["src", "type"],
    "iframe": ["width", "height", "src", "frameborder", "allow", "allowfullscreen"],
}


for TAGS in (PAGE_STRUCTURE_TAGS, META_TAGS, FORM_TAGS, ANNOYING_TAGS, MEDIA_TAGS):
    for element in TAGS:
        nh3.ALLOWED_TAGS.add(element)
        for attribute in TAGS[element]:
            if HTML_ALLOWED_ATTRIBUTES.get(element) is None:
                HTML_ALLOWED_ATTRIBUTES[element] = set()
            HTML_ALLOWED_ATTRIBUTES[element].add(attribute)

HTML_ALLOWED_ATTRIBUTES["*"] = set()
for attribute in SAFE_ATTRS:
    HTML_ALLOWED_ATTRIBUTES["*"].add(attribute)

HTML_ALLOWED_ATTRIBUTES["*"].add("class")
HTML_ALLOWED_ATTRIBUTES["*"].add("style")


def sanitize_html(html):
    return nh3.clean(
        html, 
        tags=nh3.ALLOWED_TAGS, 
        attributes=HTML_ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer nofollow",
        strip_comments=True,
        generic_attribute_prefixes={"data-"},
        url_schemes={'data', 'http', 'https', 'tel'}
    )
