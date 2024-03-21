from flask_babel import lazy_gettext as _l
from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.forms.users import (
    attach_custom_user_fields,
    attach_registration_code_field,
    attach_user_bracket_field,
    build_custom_user_fields,
    build_registration_code_field,
    build_user_bracket_field,
)


def RegistrationForm(*args, **kwargs):
    class _RegistrationForm(BaseForm):
        name = StringField(
            _l("User Name"), validators=[InputRequired()], render_kw={"autofocus": True}
        )
        email = EmailField(_l("Email"), validators=[InputRequired()])
        password = PasswordField(_l("Password"), validators=[InputRequired()])
        submit = SubmitField(_l("Submit"))

        @property
        def extra(self):
            return (
                build_custom_user_fields(
                    self, include_entries=False, blacklisted_items=()
                )
                + build_registration_code_field(self)
                + build_user_bracket_field(self)
            )

    attach_custom_user_fields(_RegistrationForm)
    attach_registration_code_field(_RegistrationForm)
    attach_user_bracket_field(_RegistrationForm)

    return _RegistrationForm(*args, **kwargs)


class LoginForm(BaseForm):
    name = StringField(
        _l("User Name or Email"),
        validators=[InputRequired()],
        render_kw={"autofocus": True},
    )
    password = PasswordField(_l("Password"), validators=[InputRequired()])
    submit = SubmitField(_l("Submit"))


class ConfirmForm(BaseForm):
    submit = SubmitField(_l("Resend Confirmation Email"))


class ResetPasswordRequestForm(BaseForm):
    email = EmailField(
        _l("Email"), validators=[InputRequired()], render_kw={"autofocus": True}
    )
    submit = SubmitField(_l("Submit"))


class ResetPasswordForm(BaseForm):
    password = PasswordField(
        _l("Password"), validators=[InputRequired()], render_kw={"autofocus": True}
    )
    submit = SubmitField(_l("Submit"))
