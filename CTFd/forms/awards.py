from wtforms import RadioField, SelectField, StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import IntegerField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm


class AwardCreationForm(BaseForm):
    name = StringField("Name")
    value = IntegerField("Value")
    category = StringField("Category")
    description = TextAreaField("Description")
    submit = SubmitField("Create")
    icon = RadioField(
        "Icon",
        choices=[
            ("", "None"),
            ("shield", "Shield"),
            ("bug", "Bug"),
            ("crown", "Crown"),
            ("crosshairs", "Crosshairs"),
            ("ban", "Ban"),
            ("lightning", "Lightning"),
            ("skull", "Skull"),
            ("brain", "Brain"),
            ("code", "Code"),
            ("cowboy", "Cowboy"),
            ("angry", "Angry"),
        ],
    )
