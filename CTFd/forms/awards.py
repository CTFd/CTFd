from wtforms import RadioField, StringField, TextAreaField
from wtforms.fields.html5 import IntegerField

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.humanize.i18n import _


class AwardCreationForm(BaseForm):
    name = StringField("Name")
    value = IntegerField("Value")
    category = StringField("Category")
    description = TextAreaField(_("forms.awards.description"))
    submit = SubmitField(_("forms.awards.create"))
    icon = RadioField(
        "Icon",
        choices=[
            ("", _("forms.awards.icon.none")),
            ("shield", _("forms.awards.icon.shield")),
            ("bug", _("forms.awards.icon.bug")),
            ("crown", _("forms.awards.icon.crown")),
            ("crosshairs", _("forms.awards.icon.crosshairs")),
            ("ban", _("forms.awards.icon.ban")),
            ("lightning", _("forms.awards.icon.lightning")),
            ("skull", _("forms.awards.icon.skull")),
            ("brain", _("forms.awards.icon.brain")),
            ("code", _("forms.awards.icon.code")),
            ("cowboy", _("forms.awards.icon.cowboy")),
            ("angry", _("forms.awards.icon.angry")),
        ],
    )
