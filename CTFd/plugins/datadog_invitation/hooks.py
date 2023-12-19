from sqlalchemy.event import listen
from CTFd.models import Users, Teams
from .controllers import DatadogInvitationController
import logging

logging.basicConfig(level=logging.DEBUG)

def on_users_create(mapper, conn, user):
    DatadogInvitationController.create_user(user.email, user.name) # Read CTFd.models.Users!

def load_hooks():
    logging.debug("registering hook on after_insert")
    listen(Users, "after_update", on_users_create)