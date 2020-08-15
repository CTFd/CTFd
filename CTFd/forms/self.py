from wtforms import PasswordField, SelectField, StringField
from wtforms.fields.html5 import DateField, URLField

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.countries import SELECT_COUNTRIES_LIST
from CTFd.models import Fields


def SettingsForm(*args, **kwargs):
    class _SettingsForm(BaseForm):
        name = StringField("User Name")
        email = StringField("Email")
        password = PasswordField("Password")
        confirm = PasswordField("Current Password")
        affiliation = StringField("Affiliation")
        website = URLField("Website")
        country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
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
        setattr(_SettingsForm, f"field-{field.id}", StringField(field.name))

    return _SettingsForm(*args, **kwargs)


class TokensForm(BaseForm):
    expiration = DateField("Expiration")
    submit = SubmitField("Generate")
