from wtforms import (
    Form,
    BooleanField,
    StringField,
    validators,
    PasswordField,
    SubmitField,
    HiddenField,
)
from CTFd.forms import BaseForm


class RegistrationForm(BaseForm):
    name = StringField("User Name")
    email = StringField("Email")
    password = PasswordField("Password")
    submit = SubmitField("Submit")
