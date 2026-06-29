from flask_babel import lazy_gettext as _l
from wtforms import BooleanField, RadioField, StringField, TextAreaField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class NotificationForm(BaseForm):
    title = StringField(_l("Title"), description=_l("Notification title"))
    content = TextAreaField(
        _l("Content"),
        description=_l("Notification contents. Can consist of HTML and/or Markdown."),
    )
    type = RadioField(
        _l("Notification Type"),
        choices=[
            ("toast", _l("Toast")),
            ("alert", _l("Alert")),
            ("background", _l("Background")),
        ],
        default="toast",
        description=_l("What type of notification users receive"),
        validators=[InputRequired()],
    )
    sound = BooleanField(
        _l("Play Sound"),
        default=True,
        description=_l("Play sound for users when they receive the notification"),
    )
    submit = SubmitField(_l("Submit"))
