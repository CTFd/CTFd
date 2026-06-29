# -*- coding: utf-8 -*-
import json
from babel.messages.pofile import read_po

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

with open('scratchpad/i18n/worklist2.json', 'w', encoding='utf-8') as f:
    json.dump(ids, f, ensure_ascii=False, indent=1)
print('wrote', len(ids), 'msgids')
