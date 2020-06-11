from wtforms import SubmitField, TextAreaField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm


class SendEmailForm(BaseForm):
    message = TextAreaField("Message", validators=[InputRequired()])
    submit = SubmitField("Send")
