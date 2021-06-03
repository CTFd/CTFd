from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from wtforms import SelectField, StringField
from wtforms.validators import InputRequired


class SubmissionSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("provided", "Provided"),
            ("id", "ID"),
            ("account_id", "Account ID"),
            ("challenge_id", "Challenge ID"),
            ("challenge_name", "Challenge Name"),
        ],
        default="provided",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")
