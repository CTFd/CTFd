from wtforms import SelectField, StringField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class SubmissionSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[("provided", "Provided"), ("id", "ID")],
        default="provided",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")
