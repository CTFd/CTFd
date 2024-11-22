from wtforms import RadioField

from CTFd.constants.languages import LANGUAGE_NAMES
from CTFd.forms import BaseForm


class LanguageForm(BaseForm):
    """Language form

    Used in core-beta theme navbar.
    """

    language = RadioField("", choices=LANGUAGE_NAMES.items())
