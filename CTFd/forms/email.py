from wtforms import StringField, TextAreaField
from wtforms.validators import InputRequired

from CTFd.constants.email import DEFAULT_USER_EMAIL_SUBJECT
from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class SendEmailForm(BaseForm):
    subject = StringField(
        "Subject", validators=[InputRequired()], default=DEFAULT_USER_EMAIL_SUBJECT
    )
    text = TextAreaField("Message", validators=[InputRequired()])
    submit = SubmitField("Send")
