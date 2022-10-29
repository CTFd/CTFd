from typing import List
from flask import session
from CTFd.models import Users
from CTFd.plugins.csaw.models import CSAWMembers
from CTFd.plugins.csaw.schema import CSAWMembersSchema


def get_members(user: Users):
    members = CSAWMembers.query.filter_by(user_id=user.id).order_by(CSAWMembers.sub_id)
    schema = CSAWMembersSchema()
    data, errors = schema.dumps(members, many=True)
    return data
