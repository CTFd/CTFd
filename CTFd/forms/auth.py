from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.forms.users import (
    attach_custom_user_fields,
    attach_registration_code_field,
    build_custom_user_fields,
    build_registration_code_field,
)

from flask_babel import lazy_gettext as _l


def RegistrationForm(*args, **kwargs):
    class _RegistrationForm(BaseForm):
        name = StringField(
            "User Name", validators=[InputRequired()], render_kw={"autofocus": True}
        )
        email = EmailField("Email", validators=[InputRequired()])
        password = PasswordField("Password", validators=[InputRequired()])
        submit = SubmitField("Submit")

        @property
        def extra(self):
            return build_custom_user_fields(
                self, include_entries=False, blacklisted_items=()
            ) + build_registration_code_field(self)

    attach_custom_user_fields(_RegistrationForm)
    attach_registration_code_field(_RegistrationForm)

    return _RegistrationForm(*args, **kwargs)


class LoginForm(BaseForm):
    name = StringField(
        _l("User Name or Email"),
        validators=[InputRequired()],
        render_kw={"autofocus": True},
    )
    password = PasswordField(
        _l("Password"), 
        validators=[InputRequired()]
    )
    submit = SubmitField(_l("Submit"))


class ConfirmForm(BaseForm):
    submit = SubmitField("Resend Confirmation Email")


class ResetPasswordRequestForm(BaseForm):
    email = EmailField(
        "Email", validators=[InputRequired()], render_kw={"autofocus": True}
    )
    submit = SubmitField("Submit")


class ResetPasswordForm(BaseForm):
    password = PasswordField(
        "Password", validators=[InputRequired()], render_kw={"autofocus": True}
    )
    submit = SubmitField("Submit")
