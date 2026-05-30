from flask_babel import lazy_gettext as _l
from wtforms import MultipleFileField, SelectField, StringField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class ChallengeSearchForm(BaseForm):
    field = SelectField(
        _l("Search Field"),
        choices=[
            ("name", _l("Name")),
            ("id", _l("ID")),
            ("category", _l("Category")),
            ("type", _l("Type")),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField(_l("Parameter"), validators=[InputRequired()])
    submit = SubmitField(_l("Search"))


class ChallengeFilesUploadForm(BaseForm):
    file = MultipleFileField(
        _l("Upload Files"),
        description=_l("Attach multiple files using Control+Click or Cmd+Click."),
        validators=[InputRequired()],
    )
    submit = SubmitField(_l("Upload"))
