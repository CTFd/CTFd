from wtforms import PasswordField, SelectField, StringField
from wtforms.fields.html5 import DateField, URLField

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.countries import SELECT_COUNTRIES_LIST


class SettingsForm(BaseForm):
    name = StringField("User Name")
    email = StringField("Email")
    password = PasswordField("Password")
    confirm = PasswordField("Current Password")
    affiliation = StringField("Affiliation")
    website = URLField("Website")
    country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
    submit = SubmitField("Submit")


class TokensForm(BaseForm):
    expiration = DateField("Expiration")
    submit = SubmitField("Generate")
