from pybluemonday import UGCPolicy

# Copied from lxml:
# https://github.com/lxml/lxml/blob/e986a9cb5d54827c59aefa8803bc90954d67221e/src/lxml/html/defs.py#L38
# fmt: off
SAFE_ATTRS = (
    'abbr', 'accept', 'accept-charset', 'accesskey', 'action', 'align',
    'alt', 'axis', 'border', 'cellpadding', 'cellspacing', 'char', 'charoff',
    'charset', 'checked', 'cite', 'class', 'clear', 'cols', 'colspan',
    'color', 'compact', 'coords', 'datetime', 'dir', 'disabled', 'enctype',
    'for', 'frame', 'headers', 'height', 'href', 'hreflang', 'hspace', 'id',
    'ismap', 'label', 'lang', 'longdesc', 'maxlength', 'media', 'method',
    'multiple', 'name', 'nohref', 'noshade', 'nowrap', 'prompt', 'readonly',
    'rel', 'rev', 'rows', 'rowspan', 'rules', 'scope', 'selected', 'shape',
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

SANITIZER = UGCPolicy()

for TAGS in (PAGE_STRUCTURE_TAGS, META_TAGS, FORM_TAGS, ANNOYING_TAGS, MEDIA_TAGS):
    for element in TAGS:
        SANITIZER.AllowElements(element)
        SANITIZER.AllowAttrs(*TAGS[element]).OnElements(element)

# Allow safe attrs copied from lxml
SANITIZER.AllowAttrs(*SAFE_ATTRS).Globally()

# Allow styling globally
SANITIZER.AllowAttrs("class", "style").Globally()

# Allow styling via bluemonday
SANITIZER.AllowStyling()

# Allow safe convenience functions from bluemonday
SANITIZER.AllowStandardAttributes()
SANITIZER.AllowStandardURLs()

# Allow data atributes
SANITIZER.AllowDataAttributes()

# Allow data URI images
SANITIZER.AllowDataURIImages()

# Link security
SANITIZER.AllowRelativeURLs(True)
SANITIZER.RequireNoFollowOnFullyQualifiedLinks(True)
SANITIZER.RequireNoFollowOnLinks(True)
SANITIZER.RequireNoReferrerOnFullyQualifiedLinks(True)
SANITIZER.RequireNoReferrerOnLinks(True)

# Allow Comments
SANITIZER.AllowComments()


def sanitize_html(html):
    return SANITIZER.sanitize(html)
