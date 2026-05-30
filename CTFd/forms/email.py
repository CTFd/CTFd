from flask_babel import lazy_gettext as _l
from wtforms import TextAreaField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class SendEmailForm(BaseForm):
    text = TextAreaField(_l("Message"), validators=[InputRequired()])
    submit = SubmitField(_l("Send"))
