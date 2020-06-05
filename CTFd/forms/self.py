from wtforms import PasswordField, StringField, SubmitField, SelectField
from wtforms.fields.html5 import DateField

from CTFd.forms import BaseForm

from CTFd.utils.countries import COUNTRIES_LIST

class SettingsForm(BaseForm):
    name = StringField("User Name")
    email = StringField("Email")
    password = PasswordField("Password")
    confirm = PasswordField("Current Password")
    affiliation = StringField("Affiliation")
    website = StringField("Website")
    country = SelectField("Country", choices=[("", "")] + COUNTRIES_LIST)
    submit = SubmitField("Submit")


class TokensForm(BaseForm):
    expiration = DateField("Expiration")
    submit = SubmitField("Generate")