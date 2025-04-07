import datetime
import functools
from pathlib import Path
from CTFd.models import Challenges, Configs, db
from CTFd.utils import get_config, set_config
from CTFd.utils.user import get_current_user, get_user_attrs, is_admin
from CTFd.utils.plugins import override_template

from flask import render_template,request,Blueprint, url_for, abort,redirect,session

class UserChallenges(db.Model):
    __tablename__ = "UserChallenges"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer,db.ForeignKey('users.id'))
    challenge = db.Column(db.Integer,db.ForeignKey('challenges.id'))
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    changed = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __init__(self,user,challenge,date):
        self.user = user
        self.challenge = challenge
        self.date = date

class UserChallenge:
    def __init__(self,id,name,category,author,value,type,state,creation,lchange):
        self.id = id
        self.name = name
        self.category = category
        self.author = author
        self.value = value
        self.type = type
        self.state = state
        self.creation = creation
        self.lastChanged = lchange



def add_User_Link(challenge_id):
    userchallenge = UserChallenges(get_current_user().id,challenge_id,datetime.datetime.utcnow())
    db.session.add(userchallenge)
    db.session.commit()

def registerTemplate(old_path, new_path):
    dir_path = Path(__file__).parent.resolve()
    template_path = dir_path/'templates'/new_path
    override_template(old_path,open(template_path).read())

def userChallenge_allowed(f):
    """
    Decorator that requires the user to be authed and userchallenges to be active
    :param f:
    :return:
    """

    @functools.wraps(f)
    def userChallenge_wrapper(*args, **kwargs):
        value = get_config('allowUserChallenges')

        if (value and get_current_user()) or is_admin():
            return f(*args, **kwargs)
        else:
            if request.content_type == "application/json":
                abort(403)
            else:
                return redirect(url_for("auth.login", next=request.full_path))
    return userChallenge_wrapper

def update_allow_challenges():

    #flip submission code

    db.session.commit()
    config = Configs.query.filter(Configs.key == "allowUserChallenges").first()
    if config:
        value = get_config('allowUserChallenges')
        if value:
            set_config('allowUserChallenges','false')
            return False
        else:
            set_config('allowUserChallenges','true')
            return True
    else:
        conf = Configs(key="allowUserChallenges",value="true")
        db.session.add(conf)
        db.session.commit()
        return True

def owned_by_user(f):
    """
    Decorator that requires the accessed challenge to be registered under the user's name
    :param f:
    :return:
    """
    @functools.wraps(f)
    def is_owned_wrapper(*args, **kwargs):
        user = db.session.query(UserChallenges.user).filter(UserChallenges.challenge == kwargs.get("challenge_id")).first()
        db.session.commit()
        if (user and get_current_user() and user[0] == get_current_user().id) or is_admin():
            return f(*args, **kwargs)
        else:
            if request.content_type == "application/json":
                abort(403)
            else:
                return redirect(url_for("auth.login", next=request.full_path))
    return is_owned_wrapper

def getAllUserChallenges(q,field):
    filters =[]
    
    if q:
        # The field exists as an exposed column
        if Challenges.__mapper__.has_property(field):
            filters.append(getattr(Challenges, field).like("%{}%".format(q)))

    filters.append(getattr(UserChallenges,'user').like(get_current_user().id))

    query = db.session.query(UserChallenges.challenge).filter(*filters)
    challenge_ids_raw = query.all()
    challenge_ids = []
    for chal in challenge_ids_raw:
        challenge_ids.append(chal[0])        
    challenges = Challenges.query.filter(Challenges.id.in_(challenge_ids)).all()
    return challenges

def getUserForChallenge(id):
    query = db.session.query(UserChallenges.user).filter(getattr(UserChallenges,'challenge').like(id)).first()
    return 'system-created' if query == None else get_user_attrs(query[0]).name

def getCreationDate(id):
    db.session.execute('alter Table UserChallenges add column if not exists date datetime')
    query = db.session.query(UserChallenges.date).filter(getattr(UserChallenges,'challenge').like(id)).first()
    db.session.commit()
    if(query == None):
        return "no date saved"
    elif (query[0]== None):
        return "no date saved"
    else:
        return query[0]
    
def getLastChanged(id):
    db.session.execute('alter Table UserChallenges add column if not exists changed datetime')
    query = db.session.query(UserChallenges.changed).filter(getattr(UserChallenges,'challenge').like(id)).first()
    db.session.commit()
    if(query == None):
        return getCreationDate(id)
    elif(query[0] == None):
        return getCreationDate(id)
    else:
        return query[0]
   
def setLastChanged(id):
    db.session.execute('alter Table UserChallenges add column if not exists changed datetime')
    time = datetime.datetime.utcnow()
    query = db.session.query(UserChallenges).filter(getattr(UserChallenges,'challenge').like(id)).first()
    if(query != None):
        setattr(query,'changed',time)
    db.session.commit()
