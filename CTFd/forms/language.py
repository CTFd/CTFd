from wtforms import RadioField

from CTFd.constants.languages import LANGUAGE_NAMES
from CTFd.forms import BaseForm


class LanguageForm(BaseForm):
    """Language form for only switching langauge without rendering all profile settings"""

    language = RadioField("", choices=LANGUAGE_NAMES.items())
