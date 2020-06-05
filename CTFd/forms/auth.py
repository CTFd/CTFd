from wtforms import PasswordField, StringField, SubmitField

from CTFd.forms import BaseForm


class RegistrationForm(BaseForm):
    name = StringField("User Name")
    email = StringField("Email")
    password = PasswordField("Password")
    submit = SubmitField("Submit")


class LoginForm(BaseForm):
    name = StringField("User Name or Email")
    password = PasswordField("Password")
    submit = SubmitField("Submit")


class ConfirmForm(BaseForm):
    submit = SubmitField("Resend")


class ResetPasswordRequestForm(BaseForm):
    email = StringField("Email")
    submit = SubmitField("Submit")


class ResetPasswordForm(BaseForm):
    password = PasswordField("Password")
    submit = SubmitField("Submit")
