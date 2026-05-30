from flask_babel import lazy_gettext as _l
from wtforms import SelectField, StringField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class SubmissionSearchForm(BaseForm):
    field = SelectField(
        _l("Search Field"),
        choices=[
            ("provided", _l("Provided")),
            ("id", _l("ID")),
            ("account_id", _l("Account ID")),
            ("challenge_id", _l("Challenge ID")),
            ("challenge_name", _l("Challenge Name")),
        ],
        default="provided",
        validators=[InputRequired()],
    )
    q = StringField(_l("Parameter"), validators=[InputRequired()])
    submit = SubmitField(_l("Search"))
