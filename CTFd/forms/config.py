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
        "Accounts",
        description="Deletes all user and team accounts and their associated information",
    )
    submissions = BooleanField(
        "Submissions",
        description="Deletes all records that accounts gained points or took an action",
    )
    challenges = BooleanField(
        "Challenges", description="Deletes all challenges and associated data"
    )
    pages = BooleanField(
        "Pages", description="Deletes all pages and their associated files"
    )
    notifications = BooleanField(
        "Notifications", description="Deletes all notifications"
    )
    submit = SubmitField("Reset CTF")


class AccountSettingsForm(BaseForm):
    domain_whitelist = StringField(
        "Email Domain Allowlist",
        description="Comma-seperated list of allowable email domains which users can register under (e.g. examplectf.com, example.com, *.example.com)",
    )
    domain_blacklist = StringField(
        "Email Domain Blocklist",
        description="Comma-seperated list of disallowed email domains which users cannot register under (e.g. examplectf.com, example.com, *.example.com)",
    )
    team_creation = SelectField(
        "Team Creation",
        description="Control whether users can create their own teams (Teams mode only)",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="true",
    )
    team_size = IntegerField(
        widget=NumberInput(min=0),
        description="Maximum number of users per team (Teams mode only)",
    )
    num_teams = IntegerField(
        "Maximum Number of Teams",
        widget=NumberInput(min=0),
        description="Maximum number of teams allowed to register with this CTF (Teams mode only)",
    )
    num_users = IntegerField(
        "Maximum Number of Users",
        widget=NumberInput(min=0),
        description="Maximum number of user accounts allowed to register with this CTF",
    )
    password_min_length = IntegerField(
        "Minimum Password Length for Users",
        widget=NumberInput(min=0),
        description="Minimum Password Length for Users",
    )
    verify_emails = SelectField(
        "Verify Emails",
        description="Control whether users must confirm their email addresses before playing",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="false",
    )
    team_disbanding = SelectField(
        "Team Disbanding",
        description="Control whether team captains are allowed to disband their own teams",
        choices=[
            ("inactive_only", "Enabled for Inactive Teams"),
            ("disabled", "Disabled"),
        ],
        default="inactive_only",
    )
    name_changes = SelectField(
        "Name Changes",
        description="Control whether users and teams can change their names",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="true",
    )
    incorrect_submissions_per_min = IntegerField(
        "Incorrect Submissions per Minute",
        widget=NumberInput(min=1),
        description="Number of submissions allowed per minute for flag bruteforce protection (default: 10)",
    )

    submit = SubmitField("Update")


class ExportCSVForm(BaseForm):
    table = SelectField("Database Table", choices=get_dumpable_tables())
    submit = SubmitField("Download CSV")


class ImportCSVForm(BaseForm):
    csv_type = SelectField(
        "CSV Type",
        choices=[("users", "Users"), ("teams", "Teams"), ("challenges", "Challenges")],
        description="Type of CSV data",
    )
    csv_file = FileField("CSV File", description="CSV file contents")


class SocialSettingsForm(BaseForm):
    social_shares = SelectField(
        "Social Shares",
        description="Enable or Disable social sharing links for challenge solves",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="true",
    )
    social_share_solve_template = TextAreaField(
        "Social Share Solve Template",
        description="HTML for Share Template",
        default=BASE_TEMPLATE,
    )
    submit = SubmitField("Update")


class LegalSettingsForm(BaseForm):
    tos_url = URLField(
        "Terms of Service URL",
        description="External URL to a Terms of Service document hosted elsewhere",
    )
    tos_text = TextAreaField(
        "Terms of Service",
        description="Text shown on the Terms of Service page",
    )
    privacy_url = URLField(
        "Privacy Policy URL",
        description="External URL to a Privacy Policy document hosted elsewhere",
    )
    privacy_text = TextAreaField(
        "Privacy Policy",
        description="Text shown on the Privacy Policy page",
    )
    submit = SubmitField("Update")


class ChallengeSettingsForm(BaseForm):
    view_self_submissions = SelectField(
        "View Self Submissions",
        description="Allow users to view their previous submissions",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="false",
    )
    max_attempts_behavior = SelectField(
        "Max Attempts Behavior",
        description="Set Max Attempts behavior to be a lockout or a timeout",
        choices=[("lockout", "lockout"), ("timeout", "timeout")],
        default="lockout",
    )
    max_attempts_timeout = IntegerField(
        "Max Attempts Timeout Duration",
        description="How long the timeout lasts in seconds for max attempts (if set to timeout). Default is 300 seconds",
        default=300,
    )
    hints_free_public_access = SelectField(
        "Hints Free Public Access",
        description="Control whether users must be logged in to see free hints (hints without cost or requirements)",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="false",
    )
    challenge_ratings = SelectField(
        "Challenge Ratings",
        description="Control who can see and submit challenge ratings",
        choices=[
            ("public", "Public (users can submit ratings and see aggregated ratings)"),
            (
                "private",
                "Private (users can submit ratings but cannot see aggregated ratings)",
            ),
            (
                "disabled",
                "Disabled (users cannot submit ratings or see aggregated ratings)",
            ),
        ],
        default="public",
    )


class VisibilitySettingsForm(BaseForm):
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
        default=ScoreVisibilityTypes.PUBLIC,
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


class LocalizationForm(BaseForm):
    default_locale = SelectField(
        "Default Language",
        description="Language to use if a user does not specify a language in their account settings. By default, CTFd will auto-detect the user's preferred language.",
        choices=SELECT_LANGUAGE_LIST,
    )


class EmailSettingsForm(BaseForm):
    # Mail Server Settings
    mailfrom_addr = StringField(
        "Mail From Address", description="Email address used to send email"
    )
    mail_server = StringField(
        "Mail Server Address",
        description="Change the email server used by CTFd to send email",
    )
    mail_port = IntegerField(
        "Mail Server Port",
        widget=NumberInput(min=1, max=65535),
        description="Mail Server Port",
    )
    mail_useauth = BooleanField("Use Mail Server Username and Password")
    mail_username = StringField("Username", description="Mail Server Account Username")
    mail_password = StringField("Password", description="Mail Server Account Password")
    mail_ssl = BooleanField("TLS/SSL")
    mail_tls = BooleanField("STARTTLS")

    # Mailgun Settings (deprecated)
    mailgun_base_url = StringField(
        "Mailgun API Base URL", description="Mailgun API Base URL"
    )
    mailgun_api_key = StringField("Mailgun API Key", description="Mailgun API Key")

    # Registration Email
    successful_registration_email_subject = StringField(
        "Subject",
        description="Subject line for registration confirmation email",
        default=DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
    )
    successful_registration_email_body = TextAreaField(
        "Body",
        description="Email body sent to users after they've finished registering",
        default=DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
    )

    # Verification Email
    verification_email_subject = StringField(
        "Subject",
        description="Subject line for account verification email",
        default=DEFAULT_VERIFICATION_EMAIL_SUBJECT,
    )
    verification_email_body = TextAreaField(
        "Body",
        description="Email body sent to users to confirm their account at the address they provided during registration",
        default=DEFAULT_VERIFICATION_EMAIL_BODY,
    )

    # Account Details Email
    user_creation_email_subject = StringField(
        "Subject",
        description="Subject line for new account details email",
        default=DEFAULT_USER_CREATION_EMAIL_SUBJECT,
    )
    user_creation_email_body = TextAreaField(
        "Body",
        description="Email body sent to new users (manually created by an admin) with their initial account details",
        default=DEFAULT_USER_CREATION_EMAIL_BODY,
    )

    # Password Reset Email
    password_reset_subject = StringField(
        "Subject",
        description="Subject line for password reset request email",
        default=DEFAULT_PASSWORD_RESET_SUBJECT,
    )
    password_reset_body = TextAreaField(
        "Body",
        description="Email body sent when a user requests a password reset",
        default=DEFAULT_PASSWORD_RESET_BODY,
    )

    # Password Reset Confirmation Email
    password_change_alert_subject = StringField(
        "Subject",
        description="Subject line for password reset confirmation email",
        default=DEFAULT_PASSWORD_CHANGE_ALERT_SUBJECT,
    )
    password_change_alert_body = TextAreaField(
        "Body",
        description="Email body sent when a user successfully resets their password",
        default=DEFAULT_PASSWORD_CHANGE_ALERT_BODY,
    )

    submit = SubmitField("Update")
