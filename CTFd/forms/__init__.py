from wtforms import Form
from wtforms import SubmitField as _SubmitField
from wtforms.csrf.core import CSRF


class CTFdCSRF(CSRF):
    def generate_csrf_token(self, csrf_token_field):
        from flask import session

        return session.get("nonce")


class BaseForm(Form):
    class Meta:
        csrf = True
        csrf_class = CTFdCSRF
        csrf_field_name = "nonce"


class SubmitField(_SubmitField):
    """
    This custom SubmitField exists because wtforms is dumb.

    See https://github.com/wtforms/wtforms/issues/205, https://github.com/wtforms/wtforms/issues/36
    The .submit() handler in JS will break if the form has an input with the name or id of "submit" so submit fields need to be changed.
    """

    def __init__(self, *args, **kwargs):
        name = kwargs.pop("name", "_submit")
        super().__init__(*args, **kwargs)
        if self.name == "submit" or name:
            self.id = name
            self.name = name


class _FormsWrapper:
    pass


Forms = _FormsWrapper()

from CTFd.forms import auth  # noqa: I001 isort:skip
from CTFd.forms import self  # noqa: I001 isort:skip
from CTFd.forms import teams  # noqa: I001 isort:skip
from CTFd.forms import setup  # noqa: I001 isort:skip
from CTFd.forms import submissions  # noqa: I001 isort:skip
from CTFd.forms import users  # noqa: I001 isort:skip
from CTFd.forms import challenges  # noqa: I001 isort:skip
from CTFd.forms import notifications  # noqa: I001 isort:skip
from CTFd.forms import config  # noqa: I001 isort:skip
from CTFd.forms import pages  # noqa: I001 isort:skip
from CTFd.forms import awards  # noqa: I001 isort:skip

Forms.auth = auth
Forms.self = self
Forms.teams = teams
Forms.setup = setup
Forms.submissions = submissions
Forms.users = users
Forms.challenges = challenges
Forms.notifications = notifications
Forms.config = config
Forms.pages = pages
Forms.awards = awards
