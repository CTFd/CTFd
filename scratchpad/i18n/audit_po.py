# -*- coding: utf-8 -*-
from babel.messages.pofile import read_po

langs = ['ru', 'de', 'es', 'fr', 'pl', 'ja', 'ar', 'zh_Hans_CN', 'zh_Hant_TW']
for lang in langs:
    p = 'CTFd/translations/%s/LC_MESSAGES/messages.po' % lang
    with open(p, 'rb') as f:
        cat = read_po(f)
    empty = same = 0
    same_examples = []
    for m in cat:
        if not m.id:
            continue
        s = m.string
        if isinstance(s, (list, tuple)):
            if any(not x for x in s):
                empty += 1
        else:
            if not s:
                empty += 1
            elif s == m.id and len(str(m.id)) > 3 and not str(m.id).startswith('%'):
                same += 1
                if len(same_examples) < 6:
                    same_examples.append(str(m.id))
    print('%s: total=%d empty=%d msgstr==msgid=%d' % (lang, len(cat), empty, same))
    if same_examples:
        for ex in same_examples:
            print('     same: %r' % ex)
