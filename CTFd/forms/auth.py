from wtforms import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import Fields


def RegistrationForm(*args, **kwargs):
    class _RegistrationForm(BaseForm):
        name = StringField("User Name", validators=[InputRequired()])
        email = EmailField("Email", validators=[InputRequired()])
        password = PasswordField("Password", validators=[InputRequired()])
        submit = SubmitField("Submit")

        @property
        def extra(self):
            fields = []
            new_fields = Fields.query.all()
            for field in new_fields:
                entry = (field.name, getattr(self, f"field-{field.id}"))
                fields.append(entry)
            return fields

    new_fields = Fields.query.all()
    for field in new_fields:
        setattr(_RegistrationForm, f"field-{field.id}", StringField(field.name))

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
