from flask import session
from wtforms import PasswordField, SelectField, StringField
from wtforms.fields.html5 import DateField, URLField

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.forms.users import attach_custom_user_fields, build_custom_user_fields
from CTFd.utils.countries import SELECT_COUNTRIES_LIST


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
            return build_custom_user_fields(
                self,
                include_entries=True,
                fields_kwargs={"editable": True},
                field_entries_kwargs={"user_id": session["id"]},
            )

    attach_custom_user_fields(_SettingsForm, editable=True)

    return _SettingsForm(*args, **kwargs)


class TokensForm(BaseForm):
    expiration = DateField("Expiration")
    submit = SubmitField("Generate")
