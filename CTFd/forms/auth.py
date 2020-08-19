from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.forms.users import attach_custom_user_fields, build_custom_user_fields


def RegistrationForm(*args, **kwargs):
    class _RegistrationForm(BaseForm):
        name = StringField("User Name", validators=[InputRequired()])
        email = EmailField("Email", validators=[InputRequired()])
        password = PasswordField("Password", validators=[InputRequired()])
        submit = SubmitField("Submit")

        @property
        def extra(self):
            return build_custom_user_fields(
                self, include_entries=False, blacklisted_items=()
            )

    attach_custom_user_fields(_RegistrationForm)

    return _RegistrationForm(*args, **kwargs)


class LoginForm(BaseForm):
    name = StringField("User Name or Email", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Submit")


class ConfirmForm(BaseForm):
    submit = SubmitField("Resend")


class ResetPasswordRequestForm(BaseForm):
    email = EmailField("Email", validators=[InputRequired()])
    submit = SubmitField("Submit")


class ResetPasswordForm(BaseForm):
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Submit")
