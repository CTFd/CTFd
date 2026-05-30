# -*- coding: utf-8 -*-
"""
Apply translated JSON maps into each language's messages.po:
  - fill empty msgstr from the JSON map
  - clear the 'fuzzy' flag on any entry we provide a translation for
Preserves everything else (existing translations, headers, comments, plurals).
"""
import json
from babel.messages.pofile import read_po, write_po

langs = ['ru', 'de', 'es', 'fr', 'pl', 'ja', 'ar', 'zh_Hans_CN', 'zh_Hant_TW']

for lang in langs:
    po_path = 'CTFd/translations/%s/LC_MESSAGES/messages.po' % lang
    tr_path = 'scratchpad/i18n/tr_%s.json' % lang
    with open(tr_path, 'r', encoding='utf-8') as f:
        tr = json.load(f)
    with open(po_path, 'rb') as f:
        cat = read_po(f)

    filled = 0
    unfuzzed = 0
    for msgid, msgstr in tr.items():
        msg = cat.get(msgid)
        if msg is None:
            # msgid not in this catalog (shouldn't happen) - skip
            print('  %s: WARNING msgid not found: %r' % (lang, msgid))
            continue
        # only fill if currently empty (don't overwrite existing translations)
        cur = msg.string
        is_empty = (not cur) if not isinstance(cur, (list, tuple)) \
            else any(not x for x in cur)
        if is_empty:
            msg.string = msgstr
            filled += 1
        if 'fuzzy' in msg.flags:
            msg.flags.discard('fuzzy')
            unfuzzed += 1

    with open(po_path, 'wb') as f:
        write_po(f, cat, width=76, sort_output=False, sort_by_file=False)
    print('%s: filled=%d unfuzzed=%d' % (lang, filled, unfuzzed))

print('done')
