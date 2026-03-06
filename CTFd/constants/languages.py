from CTFd.constants import RawEnum


class Languages(str, RawEnum):
ENGLISH = "en"
ARABIC = "ar"
BRAZILIAN_PORTUGESE = "pt_BR"
CATALAN = "ca"
CHINESE = "zh_CN"
CROATIAN = "hr"
FINNISH = "fi"
FRENCH = "fr"
GERMAN = "de"
GREEK = "el"
HEBREW = "he"
ITALIAN = "it"
JAPANESE = "ja"
KOREAN = "ko"
NORWEGIAN = "no"
POLISH = "pl"
ROMANIAN = "ro"
RUSSIAN = "ru"
SLOVAK = "sk"
SLOVENIAN = "sl"
SPANISH = "es"
SWEDISH = "sv"
TAIWANESE = "zh_TW"
UZBEK = "uz"
VIETNAMESE = "vi"


LANGUAGE_NAMES = {
    "en": "English",
    "ca": "Català",
    "de": "Deutsch",
    "es": "Español",
    "fi": "Suomi",
    "fr": "Français",
    "it": "Italiano",
    "no": "Norsk",
    "pl": "Polski",
    "pt_BR": "Português do Brasil",
    "ro": "Română",
    "sk": "Slovenský jazyk",
    "sl": "Slovenščina",
    "sv": "Svenska",
    "uz": "oʻzbekcha",
    "ar": "اَلْعَرَبِيَّةُ",
    "el": "Ελληνικά",
    "he": "עברית",
    "ja": "日本語",
    "ko": "한국어",
    "ru": "русский язык",
    "vi": "tiếng Việt",
    "zh_CN": "简体中文",
    "zh_TW": "繁體中文",
}

SELECT_LANGUAGE_LIST = [("", "")] + [
    (str(lang), LANGUAGE_NAMES.get(str(lang))) for lang in Languages
]

Languages.names = LANGUAGE_NAMES
Languages.select_list = SELECT_LANGUAGE_LIST
