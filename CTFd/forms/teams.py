from wtforms import PasswordField, SelectField, StringField, SubmitField
from wtforms.fields.html5 import DateField

from CTFd.forms import BaseForm


class TeamJoinForm(BaseForm):
    name = StringField("Team Name")
    password = PasswordField("Team Password")
    submit = SubmitField("Join")


class TeamCreateForm(BaseForm):
    name = StringField("Team Name")
    password = PasswordField("Team Password")
    submit = SubmitField("Create")