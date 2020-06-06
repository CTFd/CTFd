from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.fields.html5 import URLField

from CTFd.forms import BaseForm
from CTFd.utils.countries import SELECT_COUNTRIES_LIST


class TeamJoinForm(BaseForm):
    name = StringField("Team Name")
    password = PasswordField("Team Password")
    submit = SubmitField("Join")


class TeamCreateForm(BaseForm):
    name = StringField("Team Name")
    password = PasswordField("Team Password")
    submit = SubmitField("Create")


class TeamEditForm(BaseForm):
    name = StringField("Team Name")
    confirm = PasswordField("Current Password")
    password = PasswordField("Team Password")
    affiliation = StringField("Affiliation")
    website = URLField("Website")
    country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
    submit = SubmitField("Submit")


class TeamCaptainForm(BaseForm):
    captain_id = SelectField("Team Captain", choices=[])
    submit = SubmitField("Submit")
