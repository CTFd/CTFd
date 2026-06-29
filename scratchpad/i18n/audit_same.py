# -*- coding: utf-8 -*-
import sys
from babel.messages.pofile import read_po

lang = sys.argv[1]
p = 'CTFd/translations/%s/LC_MESSAGES/messages.po' % lang
with open(p, 'rb') as f:
    cat = read_po(f)
for m in cat:
    if not m.id:
        continue
    s = m.string
    if isinstance(s, (list, tuple)):
        continue
    if s and s == m.id and len(str(m.id)) > 3 and not str(m.id).startswith('%'):
        sys.stdout.buffer.write(('  %r\n' % str(m.id)).encode('utf-8'))
