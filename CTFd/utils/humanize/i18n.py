from CTFd.exceptions import InvalidLanguageException
from CTFd.utils.config import get_config
from CTFd.translations import translations


def _(key, *args):
    """
    translation function for backend
    to add new languages or contribute to existing ones,
        see CTFd.translations
    """
    preference = get_config("i18n_language", "en_US")
    if preference not in translations:
        raise InvalidLanguageException
    item = translations[preference].get(key, "")
    if callable(item):
        return item(*args)
    return item
