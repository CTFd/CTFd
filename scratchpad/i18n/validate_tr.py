# -*- coding: utf-8 -*-
import json

with open('scratchpad/i18n/worklist2.json', 'r', encoding='utf-8') as f:
    ids = json.load(f)
idset = set(ids)

langs = ['ru', 'de', 'es', 'fr', 'pl', 'ja', 'ar', 'zh_Hans_CN', 'zh_Hant_TW']
ok = True
for lang in langs:
    p = 'scratchpad/i18n/tr_%s.json' % lang
    try:
        with open(p, 'r', encoding='utf-8') as f:
            d = json.load(f)
    except Exception as e:
        print('%s: LOAD ERROR %s' % (lang, e))
        ok = False
        continue
    keys = set(d.keys())
    missing = idset - keys
    extra = keys - idset
    empty = [k for k, v in d.items() if not v or not str(v).strip()]
    same = [k for k, v in d.items() if str(v).strip() == k and len(k) > 5
            and k not in ('TLS/SSL', 'HTML', 'Format', 'Mailgun API Key',
                          'Mailgun API Base URL', 'Database Table')]
    status = 'OK' if (not missing and not empty) else 'PROBLEM'
    if missing or empty:
        ok = False
    print('%s: %s keys=%d missing=%d extra=%d empty=%d untranslated_like=%d'
          % (lang, status, len(d), len(missing), len(extra), len(empty), len(same)))
    if missing:
        print('   missing sample:', list(missing)[:3])
    if empty:
        print('   empty sample:', empty[:3])
    if same:
        print('   same-as-english:', same[:6])
print('---')
print('ALL OK' if ok else 'FIX NEEDED')
