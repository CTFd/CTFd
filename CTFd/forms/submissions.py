from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm


class SubmissionSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[("provided", "Provided"), ("id", "ID")],
        default="provided",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")
