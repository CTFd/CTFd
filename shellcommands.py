from CTFd.plugins.csaw.models import CSAWMembers, CSAWRegions
from CTFd.models import db, Users
from pprint import pprint
import json

# ---

Users.query.all()
non_admins = Users.query.all()[1:]

for u in non_admins:
    db.session.delete(u)

db.session.commit()

# ---

PATH_JSON_OUTPUT = "/home/yuyue/Downloads/csaw-final-data"
PATH_USERS_JSON = f"{PATH_JSON_OUTPUT}/users.json"
PATH_MEMBERS_JSON = f"{PATH_JSON_OUTPUT}/members.json"

with open(PATH_USERS_JSON) as f:
    user_list = json.load(f)

with open(PATH_MEMBERS_JSON) as f:
    member_list = json.load(f)

user_models = [Users(**d) for d in user_list]
db.session.add_all(user_models)
db.session.commit()


member_models = [CSAWMembers.fromdict(d) for d in member_list]
db.session.add_all(member_models)
db.session.commit()

