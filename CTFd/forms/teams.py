from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.fields.html5 import EmailField, URLField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.countries import SELECT_COUNTRIES_LIST


class TeamJoinForm(BaseForm):
    name = StringField("Team Name", validators=[InputRequired()])
    password = PasswordField("Team Password", validators=[InputRequired()])
    submit = SubmitField("Join")


class TeamRegisterForm(BaseForm):
    name = StringField("Team Name", validators=[InputRequired()])
    password = PasswordField("Team Password", validators=[InputRequired()])
    submit = SubmitField("Create")


class TeamSettingsForm(BaseForm):
    name = StringField("Team Name")
    confirm = PasswordField("Current Password")
    password = PasswordField("Team Password")
    affiliation = StringField("Affiliation")
    website = URLField("Website")
    country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
    submit = SubmitField("Submit")


class TeamCaptainForm(BaseForm):
    # Choices are populated dynamically at form creation time
    captain_id = SelectField("Team Captain", choices=[], validators=[InputRequired()])
    submit = SubmitField("Submit")


class TeamSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("id", "ID"),
            ("affiliation", "Affiliation"),
            ("website", "Website"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class PublicTeamSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("affiliation", "Affiliation"),
            ("website", "Website"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class TeamCreateForm(BaseForm):
    name = StringField("Team Name", validators=[InputRequired()])
    email = EmailField("Email")
    password = PasswordField("Password")
    website = URLField("Website")
    affiliation = StringField("Affiliation")
    country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
    hidden = BooleanField("Hidden")
    banned = BooleanField("Banned")
    submit = SubmitField("Submit")


class TeamEditForm(TeamCreateForm):
    pass
