from wtforms import BooleanField, SelectField, StringField
from wtforms.fields.html5 import IntegerField
from wtforms.widgets.html5 import NumberInput

from CTFd.forms import BaseForm, SubmitField


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
        "Account Email Whitelist",
        description="Comma-seperated email domains which users can register under (e.g. ctfd.io, gmail.com, yahoo.com)",
    )
    team_size = IntegerField(
        widget=NumberInput(min=0), description="Amount of users per team"
    )
    verify_emails = SelectField(
        "Verify Emails",
        description="Control whether users must confirm their email addresses before playing",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="false",
    )
    name_changes = SelectField(
        "Name Changes",
        description="Control whether users can change their names",
        choices=[("true", "Enabled"), ("false", "Disabled")],
        default="true",
    )

    submit = SubmitField("Update")
