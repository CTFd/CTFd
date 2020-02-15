"""Add default email templates

Revision ID: 1093835a1051
Revises: a03403986a32
Create Date: 2020-02-15 01:32:10.959373

"""
from alembic import op
from sqlalchemy.sql import column, table

from CTFd.models import db
from CTFd.utils.email import (
    DEFAULT_PASSWORD_RESET_BODY,
    DEFAULT_PASSWORD_RESET_SUBJECT,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
    DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
    DEFAULT_USER_CREATION_EMAIL_BODY,
    DEFAULT_USER_CREATION_EMAIL_SUBJECT,
    DEFAULT_VERIFICATION_EMAIL_BODY,
    DEFAULT_VERIFICATION_EMAIL_SUBJECT,
)

# revision identifiers, used by Alembic.
revision = "1093835a1051"
down_revision = "a03403986a32"
branch_labels = None
depends_on = None

configs_table = table(
    "config", column("id", db.Integer), column("key", db.Text), column("value", db.Text)
)


def get_config(key):
    connection = op.get_bind()
    return connection.execute(
        configs_table.select().where(configs_table.c.key == key).limit(1)
    ).fetchone()


def set_config(key, value):
    connection = op.get_bind()
    connection.execute(configs_table.insert().values(key=key, value=value))


def upgrade():
    # Only run if this instance already been setup before
    if bool(get_config("setup")) is True:
        for k, v in [
            ("password_reset_body", DEFAULT_PASSWORD_RESET_BODY),
            ("password_reset_subject", DEFAULT_PASSWORD_RESET_SUBJECT),
            (
                "successful_registration_email_body",
                DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_BODY,
            ),
            (
                "successful_registration_email_subject",
                DEFAULT_SUCCESSFUL_REGISTRATION_EMAIL_SUBJECT,
            ),
            ("user_creation_email_body", DEFAULT_USER_CREATION_EMAIL_BODY),
            ("user_creation_email_subject", DEFAULT_USER_CREATION_EMAIL_SUBJECT),
            ("verification_email_body", DEFAULT_VERIFICATION_EMAIL_BODY),
            ("verification_email_subject", DEFAULT_VERIFICATION_EMAIL_SUBJECT),
        ]:
            if get_config(k) is None:
                set_config(k, v)


def downgrade():
    pass
