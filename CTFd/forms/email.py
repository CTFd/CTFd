from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, InputRequired
from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField


class SendEmailForm(BaseForm):
    text = TextAreaField("Message", validators=[InputRequired()])
    submit = SubmitField("Send")


class EmailAllForm(BaseForm):
    subject = StringField("Subject", validators=[DataRequired()])
    body = TextAreaField("Body", validators=[DataRequired()])
    submit = SubmitField("Email All")

    def validate(self):
        if not super(EmailAllForm, self).validate():
            return False
        # Enforce plain-text only (no HTML)
        if "<" in self.body.data or ">" in self.body.data:
            self.body.errors.append("Plain text only no HTML allowed")
            return False
        return True
