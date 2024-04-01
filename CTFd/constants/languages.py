from CTFd.constants import RawEnum


class Languages(str, RawEnum):
    ENGLISH = "en"
    GERMAN = "de"
    POLISH = "pl"
    SPANISH = "es"
    ARABIC = "ar"
    CHINESE = "zh_CN"
    TAIWANESE = "zh_TW"
    FRENCH = "fr"
    KOREAN = "ko"
    RUSSIAN = "ru"
    BRAZILIAN_PORTUGESE = "pt_BR"
    SLOVAK = "sk"
    JAPANESE = "ja"
    ITALIAN = "it"
    VIETNAMESE = "vi"


LANGUAGE_NAMES = {
    "en": "English",
    "de": "Deutsch",
    "pl": "Polski",
    "es": "Español",
    "ar": "اَلْعَرَبِيَّةُ",
    "zh_CN": "中文",
    "zh_TW": "國語",
    "fr": "Français",
    "ko": "한국어",
    "ru": "русский язык",
    "pt_BR": "Português do Brasil",
    "sk": "Slovenský jazyk",
    "ja": "日本語",
    "it": "Italiano",
    "vi": "tiếng Việt",
}

SELECT_LANGUAGE_LIST = [("", "")] + [
    (str(lang), LANGUAGE_NAMES.get(str(lang))) for lang in Languages
]
