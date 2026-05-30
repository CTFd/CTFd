# -*- coding: utf-8 -*-
"""
Convert {% trans %}...{% endtrans %} that sit INSIDE an HTML attribute value
into {{ _('...') }} form. Only matches occurrences where the trans block is
the attribute value (preceded by ATTR="), leaving text-node trans blocks alone.

Handles:
  attr="{% trans %}Text{% endtrans %}"          -> attr="{{ _('Text') }}"
  attr="{% trans var=expr %}A {{ var }} B{% endtrans %}"
        -> attr="{{ _('A %(var)s B', var=expr) }}"   (single-var case)
"""
import re
import sys
import os

ATTRS = r'(?:placeholder|title|value|aria-label|aria-placeholder|alt|accept)'

# Simple case: no variables inside the trans block.
# attr="{% trans %}TEXT{% endtrans %}"
simple_re = re.compile(
    r'(' + ATTRS + r')="\{%\s*trans\s*%\}(.*?)\{%\s*endtrans\s*%\}"'
)

# Variable case: attr="{% trans v=expr %}...{{ v }}...{% endtrans %}"
var_re = re.compile(
    r'(' + ATTRS + r')="\{%\s*trans\s+(\w+)=(.*?)\s*%\}(.*?)\{%\s*endtrans\s*%\}"'
)


def esc(s):
    # escape single quotes for the python string literal
    return s.replace("\\", "\\\\").replace("'", "\\'")


def repl_simple(m):
    attr, text = m.group(1), m.group(2)
    return "%s=\"{{ _('%s') }}\"" % (attr, esc(text))


def repl_var(m):
    attr, var, expr, body = m.group(1), m.group(2), m.group(3), m.group(4)
    # turn {{ var }} inside body into %(var)s
    body2 = re.sub(r'\{\{\s*' + re.escape(var) + r'\s*\}\}', '%(' + var + ')s', body)
    return "%s=\"{{ _('%s', %s=%s) }}\"" % (attr, esc(body2), var, expr)


def process(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    orig = src
    # var case first (more specific), then simple
    src, nv = var_re.subn(repl_var, src)
    src, ns = simple_re.subn(repl_simple, src)
    if src != orig:
        with open(path, 'w', encoding='utf-8', newline='') as f:
            f.write(src)
    return nv, ns


def main():
    root = 'CTFd/themes/admin/templates'
    total_v = total_s = 0
    changed = []
    for dirpath, _dirs, files in os.walk(root):
        for fn in files:
            if not fn.endswith('.html'):
                continue
            p = os.path.join(dirpath, fn)
            nv, ns = process(p)
            if nv or ns:
                changed.append((p.replace('\\', '/'), nv, ns))
                total_v += nv
                total_s += ns
    for p, nv, ns in sorted(changed):
        print('%3d simple  %2d var   %s' % (ns, nv, p))
    print('---')
    print('TOTAL: simple=%d var=%d files=%d' % (total_s, total_v, len(changed)))


if __name__ == '__main__':
    main()
