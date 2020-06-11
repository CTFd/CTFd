from wtforms import TextAreaField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm, SubmitField


class SendEmailForm(BaseForm):
    message = TextAreaField("Message", validators=[InputRequired()])
    submit = SubmitField("Send")
