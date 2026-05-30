# -*- coding: utf-8 -*-
"""Apply round-3 translations (3 strings x 9 langs) into the .po catalogs.
Fills only empty msgstr; clears fuzzy on entries we set."""
from babel.messages.pofile import read_po, write_po

# msgid -> {lang: msgstr}
TR = {
    "standard": {
        "ru": "стандартный",
        "de": "Standard",
        "es": "estándar",
        "fr": "standard",
        "pl": "standardowy",
        "ja": "標準",
        "ar": "قياسي",
        "zh_Hans_CN": "标准",
        "zh_Hant_TW": "標準",
    },
    "dynamic": {
        "ru": "динамический",
        "de": "Dynamisch",
        "es": "dinámico",
        "fr": "dynamique",
        "pl": "dynamiczny",
        "ja": "動的",
        "ar": "ديناميكي",
        "zh_Hans_CN": "动态",
        "zh_Hant_TW": "動態",
    },
    "Require password change on next login": {
        "ru": "Требовать смену пароля при следующем входе",
        "de": "Passwortänderung bei der nächsten Anmeldung erforderlich",
        "es": "Requerir cambio de contraseña en el próximo inicio de sesión",
        "fr": "Exiger le changement de mot de passe à la prochaine connexion",
        "pl": "Wymagaj zmiany hasła przy następnym logowaniu",
        "ja": "次回ログイン時にパスワードの変更を要求する",
        "ar": "طلب تغيير كلمة المرور عند تسجيل الدخول التالي",
        "zh_Hans_CN": "下次登录时要求更改密码",
        "zh_Hant_TW": "下次登入時要求變更密碼",
    },
}

langs = ["ru", "de", "es", "fr", "pl", "ja", "ar", "zh_Hans_CN", "zh_Hant_TW"]

for lang in langs:
    po = "CTFd/translations/%s/LC_MESSAGES/messages.po" % lang
    with open(po, "rb") as f:
        cat = read_po(f)
    filled = unfuzzed = 0
    for msgid, per in TR.items():
        msg = cat.get(msgid)
        if msg is None:
            print("  %s: MISSING %r" % (lang, msgid))
            continue
        cur = msg.string
        is_empty = (not cur) if not isinstance(cur, (list, tuple)) \
            else any(not x for x in cur)
        if is_empty:
            msg.string = per[lang]
            filled += 1
        if "fuzzy" in msg.flags:
            msg.flags.discard("fuzzy")
            unfuzzed += 1
    with open(po, "wb") as f:
        write_po(f, cat, width=76, sort_output=False, sort_by_file=False)
    print("%s: filled=%d unfuzzed=%d" % (lang, filled, unfuzzed))
print("done")
