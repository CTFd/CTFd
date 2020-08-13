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
    name = StringField(
        "Team Name", description="Your team's public name shown to other competitors"
    )
    password = PasswordField(
        "New Team Password", description="Set a new team join password"
    )
    confirm = PasswordField(
        "Confirm Password",
        description="Provide your current team password (or your password) to update your team's password",
    )
    affiliation = StringField(
        "Affiliation",
        description="Your team's affiliation publicly shown to other competitors",
    )
    website = URLField(
        "Website", description="Your team's website publicly shown to other competitors"
    )
    country = SelectField(
        "Country",
        choices=SELECT_COUNTRIES_LIST,
        description="Your team's country publicly shown to other competitors",
    )
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
