from CTFd.constants import RawEnum


class Languages(str, RawEnum):
    ENGLISH = "en"
    GERMAN = "de"
    POLISH = "pl"
    SPANISH = "es"
    ARABIC = "ar"
    CHINESE_SIMPLIFIED = "zh_CN"
    CHINESE_TRADITIONAL = "zh_TW"
    FRENCH = "fr"
    KOREAN = "ko"
    RUSSIAN = "ru"
    BRAZILIAN_PORTUGESE = "pt_BR"


LANGUAGE_NAMES = {
    "en": "English",
    "de": "Deutsch",
    "pl": "Polski",
    "es": "Español",
    "ar": "اَلْعَرَبِيَّةُ",
    "zh_CN": "简体中文",
    "zh_TW": "繁體中文(中國台灣)",
    "fr": "Français",
    "ko": "한국어",
    "ru": "русский язык",
    "pt_BR": "Português do Brasil",
}

SELECT_LANGUAGE_LIST = [("", "")] + [
    (str(lang), LANGUAGE_NAMES.get(str(lang))) for lang in Languages
]
