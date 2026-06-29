from flask_babel import lazy_gettext as _l
from wtforms import BooleanField, FileField, SelectField, StringField, TextAreaField
from wtforms.fields.html5 import IntegerField, URLField
from wtforms.widgets.html5 import NumberInput

from CTFd.constants.config import (
    AccountVisibilityTypes,
    ChallengeVisibilityTypes,
    RegistrationVisibilityTypes,
    ScoreVisibilityTypes,
)
from CTFd.constants.email import (
    DEFAULT_PASSWORD_CHANGE_ALERT_BODY,
    DEFAULT_PASSWORD_CHANGE_ALERT_SUBJECT,
    DEFAULT_PASSWORD_RESET_BODY,
    DEFAULT_PASSWORD_RESET_SUBJECT,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
    DEFAULT_USER_CREATION_EMAIL_BODY,
    DEFAULT_USER_CREATION_EMAIL_SUBJECT,
    DEFAULT_VERIFICATION_EMAIL_BODY,
    DEFAULT_VERIFICATION_EMAIL_SUBJECT,
)
from CTFd.constants.languages import SELECT_LANGUAGE_LIST
from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.utils.csv import get_dumpable_tables
from CTFd.utils.social import BASE_TEMPLATE


class ResetInstanceForm(BaseForm):
    accounts = BooleanField(
        _l("Accounts"),
        description=_l(
            "Deletes all user and team accounts and their associated information"
        ),
    )
    submissions = BooleanField(
        _l("Submissions"),
        description=_l(
            "Deletes all records that accounts gained points or took an action"
        ),
    )
    challenges = BooleanField(
        _l("Challenges"), description=_l("Deletes all challenges and associated data")
    )
    pages = BooleanField(
        _l("Pages"), description=_l("Deletes all pages and their associated files")
    )
    notifications = BooleanField(
        _l("Notifications"), description=_l("Deletes all notifications")
    )
    submit = SubmitField(_l("Reset CTF"))


class AccountSettingsForm(BaseForm):
    domain_whitelist = StringField(
        _l("Email Domain Allowlist"),
        description=_l(
            "Comma-seperated list of allowable email domains which users can register under (e.g. examplectf.com, example.com, *.example.com)"
        ),
    )
    domain_blacklist = StringField(
        _l("Email Domain Blocklist"),
        description=_l(
            "Comma-seperated list of disallowed email domains which users cannot register under (e.g. examplectf.com, example.com, *.example.com)"
        ),
    )
    team_creation = SelectField(
        _l("Team Creation"),
        description=_l(
            "Control whether users can create their own teams (Teams mode only)"
        ),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="true",
    )
    team_size = IntegerField(
        widget=NumberInput(min=0),
        description=_l("Maximum number of users per team (Teams mode only)"),
    )
    num_teams = IntegerField(
        _l("Maximum Number of Teams"),
        widget=NumberInput(min=0),
        description=_l(
            "Maximum number of teams allowed to register with this CTF (Teams mode only)"
        ),
    )
    num_users = IntegerField(
        _l("Maximum Number of Users"),
        widget=NumberInput(min=0),
        description=_l(
            "Maximum number of user accounts allowed to register with this CTF"
        ),
    )
    password_min_length = IntegerField(
        _l("Minimum Password Length for Users"),
        widget=NumberInput(min=0),
        description=_l("Minimum Password Length for Users"),
    )
    verify_emails = SelectField(
        _l("Verify Emails"),
        description=_l(
            "Control whether users must confirm their email addresses before playing"
        ),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="false",
    )
    team_disbanding = SelectField(
        _l("Team Disbanding"),
        description=_l(
            "Control whether team captains are allowed to disband their own teams"
        ),
        choices=[
            ("inactive_only", _l("Enabled for Inactive Teams")),
            ("disabled", _l("Disabled")),
        ],
        default="inactive_only",
    )
    name_changes = SelectField(
        _l("Name Changes"),
        description=_l("Control whether users and teams can change their names"),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="true",
    )
    incorrect_submissions_per_min = IntegerField(
        _l("Incorrect Submissions per Minute"),
        widget=NumberInput(min=1),
        description=_l(
            "Number of submissions allowed per minute for flag bruteforce protection (default: 10)"
        ),
    )

    submit = SubmitField(_l("Update"))


class ExportCSVForm(BaseForm):
    table = SelectField(_l("Database Table"), choices=get_dumpable_tables())
    submit = SubmitField(_l("Download CSV"))


class ImportCSVForm(BaseForm):
    csv_type = SelectField(
        _l("CSV Type"),
        choices=[
            ("users", _l("Users")),
            ("teams", _l("Teams")),
            ("users+teams", _l("Users with Teams")),
            ("challenges", _l("Challenges")),
        ],
        description=_l("Type of CSV data"),
    )
    csv_file = FileField(_l("CSV File"), description=_l("CSV file contents"))


class SocialSettingsForm(BaseForm):
    social_shares = SelectField(
        _l("Social Shares"),
        description=_l(
            "Enable or Disable social sharing links for challenge solves"
        ),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="true",
    )
    social_share_solve_template = TextAreaField(
        _l("Social Share Solve Template"),
        description=_l("HTML for Share Template"),
        default=BASE_TEMPLATE,
    )
    submit = SubmitField(_l("Update"))


class LegalSettingsForm(BaseForm):
    tos_url = URLField(
        _l("Terms of Service URL"),
        description=_l(
            "External URL to a Terms of Service document hosted elsewhere"
        ),
    )
    tos_text = TextAreaField(
        _l("Terms of Service"),
        description=_l("Text shown on the Terms of Service page"),
    )
    privacy_url = URLField(
        _l("Privacy Policy URL"),
        description=_l(
            "External URL to a Privacy Policy document hosted elsewhere"
        ),
    )
    privacy_text = TextAreaField(
        _l("Privacy Policy"),
        description=_l("Text shown on the Privacy Policy page"),
    )
    submit = SubmitField(_l("Update"))


class ChallengeSettingsForm(BaseForm):
    view_self_submissions = SelectField(
        _l("View Self Submissions"),
        description=_l("Allow users to view their previous submissions"),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="false",
    )
    max_attempts_behavior = SelectField(
        _l("Max Attempts Behavior"),
        description=_l("Set Max Attempts behavior to be a lockout or a timeout"),
        choices=[("lockout", _l("lockout")), ("timeout", _l("timeout"))],
        default="lockout",
    )
    max_attempts_timeout = IntegerField(
        _l("Max Attempts Timeout Duration"),
        description=_l(
            "How long the timeout lasts in seconds for max attempts (if set to timeout). Default is 300 seconds"
        ),
        default=300,
    )
    hints_free_public_access = SelectField(
        _l("Hints Free Public Access"),
        description=_l(
            "Control whether users must be logged in to see free hints (hints without cost or requirements)"
        ),
        choices=[("true", _l("Enabled")), ("false", _l("Disabled"))],
        default="false",
    )
    challenge_ratings = SelectField(
        _l("Challenge Ratings"),
        description=_l("Control who can see and submit challenge ratings"),
        choices=[
            (
                "public",
                _l("Public (users can submit ratings and see aggregated ratings)"),
            ),
            (
                "private",
                _l(
                    "Private (users can submit ratings but cannot see aggregated ratings)"
                ),
            ),
            (
                "disabled",
                _l(
                    "Disabled (users cannot submit ratings or see aggregated ratings)"
                ),
            ),
        ],
        default="public",
    )


class VisibilitySettingsForm(BaseForm):
    challenge_visibility = SelectField(
        _l("Challenge Visibility"),
        description=_l(
            "Control whether users must be logged in to see challenges"
        ),
        choices=[
            (ChallengeVisibilityTypes.PUBLIC, _l("Public")),
            (ChallengeVisibilityTypes.PRIVATE, _l("Private")),
            (ChallengeVisibilityTypes.ADMINS, _l("Admins Only")),
        ],
        default=ChallengeVisibilityTypes.PRIVATE,
    )
    account_visibility = SelectField(
        _l("Account Visibility"),
        description=_l(
            "Control whether accounts (users & teams) are shown to everyone, only to authenticated users, or only to admins"
        ),
        choices=[
            (AccountVisibilityTypes.PUBLIC, _l("Public")),
            (AccountVisibilityTypes.PRIVATE, _l("Private")),
            (AccountVisibilityTypes.ADMINS, _l("Admins Only")),
        ],
        default=AccountVisibilityTypes.PUBLIC,
    )
    score_visibility = SelectField(
        _l("Score Visibility"),
        description=_l(
            "Control whether solves/score are shown to the public, to logged in users, hidden to all non-admins, or only shown to admins"
        ),
        choices=[
            (ScoreVisibilityTypes.PUBLIC, _l("Public")),
            (ScoreVisibilityTypes.PRIVATE, _l("Private")),
            (ScoreVisibilityTypes.HIDDEN, _l("Hidden")),
            (ScoreVisibilityTypes.ADMINS, _l("Admins Only")),
        ],
        default=ScoreVisibilityTypes.PUBLIC,
    )
    registration_visibility = SelectField(
        _l("Registration Visibility"),
        description=_l(
            "Control whether registration is enabled for everyone or disabled"
        ),
        choices=[
            (RegistrationVisibilityTypes.PUBLIC, _l("Public")),
            (RegistrationVisibilityTypes.PRIVATE, _l("Private")),
            (RegistrationVisibilityTypes.MLC, _l("MajorLeagueCyber Only")),
        ],
        default=RegistrationVisibilityTypes.PUBLIC,
    )


class LocalizationForm(BaseForm):
    default_locale = SelectField(
        _l("Default Language"),
        description=_l(
            "Language to use if a user does not specify a language in their account settings. By default, CTFd will auto-detect the user's preferred language."
        ),
        choices=SELECT_LANGUAGE_LIST,
    )


class EmailSettingsForm(BaseForm):
    # Mail Server Settings
    mailfrom_addr = StringField(
        _l("Mail From Address"), description=_l("Email address used to send email")
    )
    mail_server = StringField(
        _l("Mail Server Address"),
        description=_l("Change the email server used by CTFd to send email"),
    )
    mail_port = IntegerField(
        _l("Mail Server Port"),
        widget=NumberInput(min=1, max=65535),
        description=_l("Mail Server Port"),
    )
    mail_useauth = BooleanField(_l("Use Mail Server Username and Password"))
    mail_username = StringField(
        _l("Username"), description=_l("Mail Server Account Username")
    )
    mail_password = StringField(
        _l("Password"), description=_l("Mail Server Account Password")
    )
    mail_ssl = BooleanField(_l("TLS/SSL"))
    mail_tls = BooleanField(_l("STARTTLS"))

    # Mailgun Settings (deprecated)
    mailgun_base_url = StringField(
        _l("Mailgun API Base URL"), description=_l("Mailgun API Base URL")
    )
    mailgun_api_key = StringField(
        _l("Mailgun API Key"), description=_l("Mailgun API Key")
    )

    # Registration Email
    successful_registration_email_subject = StringField(
        _l("Subject"),
        description=_l("Subject line for registration confirmation email"),
        default=DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
    )
    successful_registration_email_body = TextAreaField(
        _l("Body"),
        description=_l(
            "Email body sent to users after they've finished registering"
        ),
        default=DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
    )

    # Verification Email
    verification_email_subject = StringField(
        _l("Subject"),
        description=_l("Subject line for account verification email"),
        default=DEFAULT_VERIFICATION_EMAIL_SUBJECT,
    )
    verification_email_body = TextAreaField(
        _l("Body"),
        description=_l(
            "Email body sent to users to confirm their account at the address they provided during registration"
        ),
        default=DEFAULT_VERIFICATION_EMAIL_BODY,
    )

    # Account Details Email
    user_creation_email_subject = StringField(
        _l("Subject"),
        description=_l("Subject line for new account details email"),
        default=DEFAULT_USER_CREATION_EMAIL_SUBJECT,
    )
    user_creation_email_body = TextAreaField(
        _l("Body"),
        description=_l(
            "Email body sent to new users (manually created by an admin) with their initial account details"
        ),
        default=DEFAULT_USER_CREATION_EMAIL_BODY,
    )

    # Password Reset Email
    password_reset_subject = StringField(
        _l("Subject"),
        description=_l("Subject line for password reset request email"),
        default=DEFAULT_PASSWORD_RESET_SUBJECT,
    )
    password_reset_body = TextAreaField(
        _l("Body"),
        description=_l("Email body sent when a user requests a password reset"),
        default=DEFAULT_PASSWORD_RESET_BODY,
    )

    # Password Reset Confirmation Email
    password_change_alert_subject = StringField(
        _l("Subject"),
        description=_l("Subject line for password reset confirmation email"),
        default=DEFAULT_PASSWORD_CHANGE_ALERT_SUBJECT,
    )
    password_change_alert_body = TextAreaField(
        _l("Body"),
        description=_l(
            "Email body sent when a user successfully resets their password"
        ),
        default=DEFAULT_PASSWORD_CHANGE_ALERT_BODY,
    )

    submit = SubmitField(_l("Update"))
