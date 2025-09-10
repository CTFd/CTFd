
from CTFd.plugins.emailnotifications.forms import settings
from CTFd.plugins.emailnotifications.forms import users

class _FormsWrapper:
    pass

forms = _FormsWrapper()

forms.settings = settings
forms.users = users