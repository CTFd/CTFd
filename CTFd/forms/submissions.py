from wtforms import SelectField, StringField, SubmitField

from CTFd.forms import BaseForm


class SubmissionSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[("provided", "Provided"), ("id", "ID")],
        default="provided",
    )
    q = StringField("Parameter")
    submit = SubmitField("Search")
