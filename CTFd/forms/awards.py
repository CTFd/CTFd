from flask_babel import lazy_gettext as _l
from wtforms import RadioField, StringField, TextAreaField
from wtforms.fields.html5 import IntegerField

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class AwardCreationForm(BaseForm):
    name = StringField(_l("Name"))
    value = IntegerField(_l("Value"))
    category = StringField(_l("Category"))
    description = TextAreaField(_l("Description"))
    submit = SubmitField(_l("Create"))
    icon = RadioField(
        _l("Icon"),
        choices=[
            ("", _l("None")),
            ("shield", _l("Shield")),
            ("bug", _l("Bug")),
            ("crown", _l("Crown")),
            ("crosshairs", _l("Crosshairs")),
            ("ban", _l("Ban")),
            ("lightning", _l("Lightning")),
            ("skull", _l("Skull")),
            ("brain", _l("Brain")),
            ("code", _l("Code")),
            ("cowboy", _l("Cowboy")),
            ("angry", _l("Angry")),
        ],
    )
