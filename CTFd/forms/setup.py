from flask_babel import lazy_gettext as _l
from wtforms import (
    FileField,
    HiddenField,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired
from wtforms.widgets.html5 import NumberInput

from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
)
from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.config import get_themes


class SetupForm(BaseForm):
    ctf_name = StringField(
        _l("Event Name"), description=_l("The name of your CTF event/workshop")
    )
    ctf_description = TextAreaField(
        _l("Event Description"), description=_l("Description for the CTF")
    )
    user_mode = RadioField(
        _l("User Mode"),
        choices=[("teams", _l("Team Mode")), ("users", _l("User Mode"))],
        default="teams",
        description=_l(
            "Controls whether users join together in teams to play (Team Mode) or play as themselves (User Mode)"
        ),
        validators=[InputRequired()],
    )

    name = StringField(
        _l("Admin Username"),
        description=_l("Your username for the administration account"),
        validators=[InputRequired()],
    )
    email = EmailField(
        _l("Admin Email"),
        description=_l("Your email address for the administration account"),
        validators=[InputRequired()],
    )
    password = PasswordField(
        _l("Admin Password"),
        description=_l("Your password for the administration account"),
        validators=[InputRequired()],
    )

    ctf_logo = FileField(
        _l("Logo"),
        description=_l(
            "Logo to use for the website instead of a CTF name. Used as the home page button. Optional."
        ),
    )
    ctf_banner = FileField(
        _l("Banner"), description=_l("Banner to use for the homepage. Optional.")
    )
    ctf_small_icon = FileField(
        _l("Small Icon"),
        description=_l(
            "favicon used in user's browsers. Only PNGs accepted. Must be 32x32px. Optional."
        ),
    )
    ctf_theme = SelectField(
        _l("Theme"),
        description=_l("CTFd Theme to use. Can be changed later."),
        choices=list(zip(get_themes(), get_themes())),
        ## TODO: Replace back to DEFAULT_THEME (aka core) in CTFd 4.0
        default="core-beta",
        validators=[InputRequired()],
    )
    theme_color = HiddenField(
        _l("Theme Color"),
        description=_l(
            "Color used by theme to control aesthetics. Requires theme support. Optional."
        ),
    )

    verify_emails = SelectField(
        _l("Verify Emails"),
        description="Control whether users must confirm their email addresses before participating",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="false",
    )
    team_size = IntegerField(
        widget=NumberInput(min=0),
        description="Amount of users per team (Teams mode only) Optional.",
    )
    challenge_visibility = SelectField(
        "Challenge Visibility",
        description="Control whether users must be logged in to see challenges",
        choices=[
            (ChallengeVisibilityTypes.PUBLIC, "Public"),
            (ChallengeVisibilityTypes.PRIVATE, "Private"),
            (ChallengeVisibilityTypes.ADMINS, "Admins Only"),
        ],
        default=ChallengeVisibilityTypes.PRIVATE,
    )
    account_visibility = SelectField(
        "Account Visibility",
        description="Control whether accounts (users & teams) are shown to everyone, only to authenticated users, or only to admins",
        choices=[
            (AccountVisibilityTypes.PUBLIC, "Public"),
            (AccountVisibilityTypes.PRIVATE, "Private"),
            (AccountVisibilityTypes.ADMINS, "Admins Only"),
        ],
        default=AccountVisibilityTypes.PUBLIC,
    )
    score_visibility = SelectField(
        "Score Visibility",
        description="Control whether solves/score are shown to the public, to logged in users, hidden to all non-admins, or only shown to admins",
        choices=[
            (ScoreVisibilityTypes.PUBLIC, "Public"),
            (ScoreVisibilityTypes.PRIVATE, "Private"),
            (ScoreVisibilityTypes.HIDDEN, "Hidden"),
            (ScoreVisibilityTypes.ADMINS, "Admins Only"),
        ],
        default=AccountVisibilityTypes.PUBLIC,
    )
    registration_visibility = SelectField(
        "Registration Visibility",
        description="Control whether registration is enabled for everyone or disabled",
        choices=[
            (RegistrationVisibilityTypes.PUBLIC, "Public"),
            (RegistrationVisibilityTypes.PRIVATE, "Private"),
            (RegistrationVisibilityTypes.MLC, "MajorLeagueCyber Only"),
        ],
        default=RegistrationVisibilityTypes.PUBLIC,
    )

    start = StringField(
        _l("Start Time"),
        description=_l("Time when your CTF is scheduled to start. Optional."),
    )
    end = StringField(
        _l("End Time"),
        description=_l("Time when your CTF is scheduled to end. Optional."),
    )
    submit = SubmitField(_l("Finish"))
