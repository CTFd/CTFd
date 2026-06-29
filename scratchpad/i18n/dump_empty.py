# -*- coding: utf-8 -*-
import sys
from babel.messages.pofile import read_po

# Use ru as the reference for which msgids are empty (same set across langs)
p = 'CTFd/translations/ru/LC_MESSAGES/messages.po'
with open(p, 'rb') as f:
    cat = read_po(f)
ids = []
for m in cat:
    if not m.id:
        continue
    s = m.string
    if isinstance(s, (list, tuple)):
        if any(not x for x in s):
            ids.append(m.id)
    elif not s:
        ids.append(m.id)
for i in ids:
    sys.stdout.buffer.write(('%r\n' % (i,)).encode('utf-8'))
