from wtforms import PasswordField, StringField, SubmitField

from CTFd.forms import BaseForm


class RegistrationForm(BaseForm):
    name = StringField("User Name")
    email = StringField("Email")
    password = PasswordField("Password")
    submit = SubmitField("Submit")
