from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from wtforms import TextAreaField
from wtforms.validators import InputRequired


class SendEmailForm(BaseForm):
    text = TextAreaField("Message", validators=[InputRequired()])
    submit = SubmitField("Send")
