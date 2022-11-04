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
from CTFd.utils.humanize.i18n import _


def RegistrationForm(*args, **kwargs):
    class _RegistrationForm(BaseForm):
        name = StringField(
            _("forms.auth.username"), validators=[InputRequired()], render_kw={"autofocus": True}
        )
        email = EmailField(_("forms.auth.email"), validators=[InputRequired()])
        password = PasswordField(_("forms.auth.password"), validators=[InputRequired()])
        submit = SubmitField(_("forms.submit"))

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
        _("forms.auth.username_or_email"),
        validators=[InputRequired()],
        render_kw={"autofocus": True},
    )
    password = PasswordField(_("forms.auth.password"), validators=[InputRequired()])
    submit = SubmitField(_("forms.submit"))


class ConfirmForm(BaseForm):
    submit = SubmitField(_("forms.auth.resend_confirm_email"))


class ResetPasswordRequestForm(BaseForm):
    email = EmailField(
        "Email", validators=[InputRequired()], render_kw={"autofocus": True}
    )
    submit = SubmitField(_("forms.submit"))


class ResetPasswordForm(BaseForm):
    password = PasswordField(
        "Password", validators=[InputRequired()], render_kw={"autofocus": True}
    )
    submit = SubmitField(_("forms.submit"))
