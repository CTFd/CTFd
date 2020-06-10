from wtforms import PasswordField, StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm


class SendEmailForm(BaseForm):
    message = TextAreaField("Message")
    submit = SubmitField("Send")
