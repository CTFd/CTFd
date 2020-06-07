from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm


class ChallengeSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("id", "ID"),
            ("category", "Category"),
            ("type", "Type"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")
