from flask_restplus import Namespace, Resource
from CTFd.models import db, Challenges, Unlocks, Hints
from CTFd.plugins.challenges import get_chal_class
from CTFd.utils.dates import ctf_ended
from CTFd.utils.decorators import during_ctf_time_only, require_verified_emails
from sqlalchemy.sql import or_

statistics_namespace = Namespace('statistics', description="Endpoint to retrieve Statistics")

from CTFd.api.v1.statistics import challenges
from CTFd.api.v1.statistics import teams
from CTFd.api.v1.statistics import users
from CTFd.api.v1.statistics import submissions
