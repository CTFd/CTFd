from wtforms import MultipleFileField, SelectField, StringField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.humanize.i18n import _


class ChallengeSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", _("challenges.name")),
            ("id", _("challenges.id")),
            ("category", _("challenges.category")),
            ("type", _("challenges.type")),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField(_("forms.parameter"), validators=[InputRequired()])
    submit = SubmitField(_("forms.search"))


class ChallengeFilesUploadForm(BaseForm):
    file = MultipleFileField(
        _("forms.challenge_files.files"),
        description=_("forms.challenge_files.files.desc"),
        validators=[InputRequired()],
    )
    submit = SubmitField(_("forms.upload"))
