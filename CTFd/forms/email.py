from wtforms import TextAreaField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class SendEmailForm(BaseForm):
    message = TextAreaField("Message", validators=[InputRequired()])
    submit = SubmitField("Send")
