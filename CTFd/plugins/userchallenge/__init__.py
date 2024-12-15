import json
from flask import render_template,request,Blueprint, url_for, abort,redirect
from sqlalchemy.sql import and_
from pathlib import Path
from CTFd.utils.plugins import override_template
from CTFd.utils.helpers.models import build_model_filters
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.plugins.flags import FLAG_CLASSES,get_flag_class
from CTFd.utils.user import get_current_user,is_admin, authed,get_current_team_attrs,get_current_user_attrs,get_current_team
from CTFd.models import Challenges, Solves, Flags, db, Configs,Hints,HintUnlocks,Flags,Submissions
from CTFd.utils.decorators import authed_only, admins_only
from CTFd.schemas.flags import FlagSchema
from CTFd.schemas.hints import HintSchema
from CTFd.schemas.tags import TagSchema
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.cache import clear_challenges,clear_standings
from CTFd.utils import config, get_config
from CTFd.utils.dates import ctf_ended
from CTFd.utils.logging import log
from CTFd.utils.challenges import (
    get_all_challenges,
    get_solve_counts_for_challenges,
    get_solve_ids_for_user_id,
    get_solves_for_challenge_id
)
from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
    scores_visible
)
import functools
import CTFd.plugins.userchallenge.apiModding as apiModding


userChallenge = Blueprint('userchallenge',__name__,template_folder='templates',static_folder ='staticAssets')

class UserChallenges(db.Model):
    __tablename__ = "UserChallenges"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer,db.ForeignKey('users.id'))
    challenge = db.Column(db.Integer,db.ForeignKey('challenges.id'))


    def __init__(self,user,challenge):
        self.user = user
        self.challenge = challenge

def add_User_Link(challenge_id):
    userchallenge = UserChallenges(get_current_user().id,challenge_id)
    db.session.add(userchallenge)
    db.session.commit()

def registerTemplate(old_path, new_path):
    dir_path = Path(__file__).parent.resolve()
    template_path = dir_path/'templates'/new_path
    override_template(old_path,open(template_path).read())
def update_allow_challenges():
    db.session.commit()
    config = Configs.query.filter(Configs.key == "allowUserChallenges").first()

    if config:
        value = config.value
        if value == "true":
            
            config.value = "false"
            db.session.commit()
            return False
        else:
            config.value = "true"
            db.session.commit()
            return True
    else:
        conf = Configs(key="allowUserChallenges",value="true")
        db.session.add(conf)
        db.session.commit()
        return True

def userChallenge_allowed(f):
    """
    Decorator that requires the user to be authed and userchallenges to be active
    :param f:
    :return:
    """

    @functools.wraps(f)
    def userChallenge_wrapper(*args, **kwargs):
        value = get_config("allowUserChallenges")
        if (value and get_current_user()) or is_admin():
            return f(*args, **kwargs)
        else:
            if request.content_type == "application/json":
                abort(403)
            else:
                return redirect(url_for("auth.login", next=request.full_path))
    return userChallenge_wrapper

def load(app):

    app.db.create_all()
    app.register_blueprint(userChallenge,url_prefix='/userchallenge')

    registerTemplate('users/private.html','newUserPage.html')



    @app.route('/admin/userChallenge')
    @admins_only
    def view_config():        
        key = Configs.query.filter(Configs.key == "allowUserChallenges").first().value
        db.session.commit()

        if key:
            if key == "true":
                enabled = "enabled"
            else :
                enabled = "disabled"
        else:
            enabled = "non-existant"
                
        return render_template('userConfig.html',enabled = enabled)
    
    @app.route('/userchallenge/api/config',methods=['GET','POST'])
    @admins_only
    def getConfig():
        newstate = update_allow_challenges()
        data = "disabled"
        if newstate:
            data = "enabled"
        return {"success":True,"data":data}

    @app.route('/userchallenge/challenges',methods=['GET',''])
    @userChallenge_allowed
    @authed_only
    def view_challenges():
        #TODO: add custom html extension of admin/challenges/challenges
        #      change methods to check for rights and only display challenges by user
        #      add custom html to change challenge editing to be available to users
        #
        #      add other plugin to modify challenge creation?                    

        q = request.args.get("q")
        field = request.args.get("field") 
        filters =[]
        if q:
            # The field exists as an exposed column
            if Challenges.__mapper__.has_property(field):
                filters.append(getattr(Challenges, field).like("%{}%".format(q)))
        
        query = db.session.query(UserChallenges.challenge).filter_by(user=get_current_user().id)
        challenge_ids_raw = query.all()
        challenge_ids = []
        for chal in challenge_ids_raw:
            challenge_ids.append(chal[0])        
        challenges = Challenges.query.filter(Challenges.id.in_(challenge_ids)).all()
        total = query.count()

        #return render_template('userChallenges.html',challenges=challenges,total=total,q=q,field=field)
        return render_template('userChallenges.html',challenges=challenges,total = total,q=q,field=field)    
    
    @app.route('/userchallenge/challenges/new',methods=['GET'])
    @userChallenge_allowed
    @authed_only
    def view_newChallenge():
        types = CHALLENGE_CLASSES.keys()
        return render_template('createUserChallenge.html',types=types)
    
    @userChallenge.add_app_template_global
    @userChallenge_allowed
    @authed_only
    @app.route('/userchallenge/challenges/<int:challenge_id>',methods=['GET'])
    #@userChallenge_allowed
    def updateChallenge(challenge_id):
        #TODO: update logic to work with plugin   
        challenges = dict(
        Challenges.query.with_entities(Challenges.id, Challenges.name).all()
        )
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        solves = (
            Solves.query.filter_by(challenge_id=challenge.id)
            .order_by(Solves.date.asc())
            .all()
        )
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()

        try:
            challenge_class = get_chal_class(challenge.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({challenge.type}) is not installed. This challenge can not be loaded.",
            )

        update_j2 = render_template(
            challenge_class.templates["update"].lstrip("/admin/challenges/"), challenge=challenge
        )

        update_script = url_for(
            "views.static_html", route=challenge_class.scripts["update"].lstrip("/admin/challenges/")
        )
        return render_template(
            "editUserChallenge.html",
            update_template=update_j2,
            update_script=update_script,
            challenge=challenge,
            challenges=challenges,
            solves=solves,
            flags=flags,
        )
    
    # api rerouting
    ## challenges
    @app.route('/userchallenge/api/challenges/',methods=['POST','GET'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def challengepost():
        data = request.form or request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge_type = data["type"]
        challenge_class = get_chal_class(challenge_type)
        challenge = challenge_class.create(request)

        add_User_Link(challenge.id)

        response = challenge_class.read(challenge)

        clear_challenges()

        return {"success": True, "data": response}

    ## singular challenge
    @app.route('/userchallenge/api/challenges/<challenge_id>',methods=['PATCH'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def idchallpatch(challenge_id):
        data = request.get_json()

        # Load data through schema for validation but not for insertion
        schema = ChallengeSchema()
        response = schema.load(data)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        challenge_class = get_chal_class(challenge.type)
        challenge = challenge_class.update(challenge, request)
        response = challenge_class.read(challenge)

        clear_standings()
        clear_challenges()

        return {"success": True, "data": response}
    @app.route('/userchallenge/api/challenges/<challenge_id>',methods=['GET'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def idchallget(challenge_id):
        if is_admin():
            chal = Challenges.query.filter(Challenges.id == challenge_id).first_or_404()
        else:
            chal = Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden", Challenges.state != "locked"),
            ).first_or_404()

        try:
            chal_class = get_chal_class(chal.type)
        except KeyError:
            abort(
                500,
                f"The underlying challenge type ({chal.type}) is not installed. This challenge can not be loaded.",
            )

        if chal.requirements:
            requirements = chal.requirements.get("prerequisites", [])
            anonymize = chal.requirements.get("anonymize")
            # Gather all challenge IDs so that we can determine invalid challenge prereqs
            all_challenge_ids = {
                c.id for c in Challenges.query.with_entities(Challenges.id).all()
            }
            if challenges_visible():
                user = get_current_user()
                if user:
                    solve_ids = (
                        Solves.query.with_entities(Solves.challenge_id)
                        .filter_by(account_id=user.account_id)
                        .order_by(Solves.challenge_id.asc())
                        .all()
                    )
                else:
                    # We need to handle the case where a user is viewing challenges anonymously
                    solve_ids = []
                solve_ids = {value for value, in solve_ids}
                prereqs = set(requirements).intersection(all_challenge_ids)
                if solve_ids >= prereqs or is_admin():
                    pass
                else:
                    if anonymize:
                        return {
                            "success": True,
                            "data": {
                                "id": chal.id,
                                "type": "hidden",
                                "name": "???",
                                "value": 0,
                                "solves": None,
                                "solved_by_me": False,
                                "category": "???",
                                "tags": [],
                                "template": "",
                                "script": "",
                            },
                        }
                    abort(403)
            else:
                abort(403)

        tags = [
            tag["value"] for tag in TagSchema("user", many=True).dump(chal.tags).data
        ]

        unlocked_hints = set()
        hints = []
        if authed():
            user = get_current_user()
            team = get_current_team()

            # TODO: Convert this into a re-useable decorator
            if is_admin():
                pass
            else:
                if config.is_teams_mode() and team is None:
                    abort(403)

            unlocked_hints = {
                u.target
                for u in HintUnlocks.query.filter_by(
                    type="hints", account_id=user.account_id
                )
            }
            files = []
            for f in chal.files:
                token = {
                    "user_id": user.id,
                    "team_id": team.id if team else None,
                    "file_id": f.id,
                }
                files.append(
                    url_for("views.files", path=f.location, token=serialize(token))
                )
        else:
            files = [url_for("views.files", path=f.location) for f in chal.files]

        for hint in Hints.query.filter_by(challenge_id=chal.id).all():
            if hint.id in unlocked_hints or ctf_ended():
                hints.append(
                    {"id": hint.id, "cost": hint.cost, "content": hint.content}
                )
            else:
                hints.append({"id": hint.id, "cost": hint.cost})

        response = chal_class.read(challenge=chal)

        # Get list of solve_ids for current user
        if authed():
            user = get_current_user()
            user_solves = get_solve_ids_for_user_id(user_id=user.id)
        else:
            user_solves = []

        solves_count = get_solve_counts_for_challenges(challenge_id=chal.id)
        if solves_count:
            challenge_id = chal.id
            solve_count = solves_count.get(chal.id)
            solved_by_user = challenge_id in user_solves
        else:
            solve_count, solved_by_user = 0, False

        # Hide solve counts if we are hiding solves/accounts
        if scores_visible() is False or accounts_visible() is False:
            solve_count = None

        if authed():
            # Get current attempts for the user
            attempts = Submissions.query.filter_by(
                account_id=user.account_id, challenge_id=challenge_id
            ).count()
        else:
            attempts = 0

        response["solves"] = solve_count
        response["solved_by_me"] = solved_by_user
        response["attempts"] = attempts
        response["files"] = files
        response["tags"] = tags
        response["hints"] = hints

        response["view"] = render_template(
            chal_class.templates["view"].lstrip("/"),
            solves=solve_count,
            solved_by_me=solved_by_user,
            files=files,
            tags=tags,
            hints=[Hints(**h) for h in hints],
            max_attempts=chal.max_attempts,
            attempts=attempts,
            challenge=chal,
        )

        db.session.close()
        return {"success": True, "data": response}
    
    ## types
    @app.route('/app/api/challenges/types')
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def typeget():
        response = {}

        for class_id in CHALLENGE_CLASSES:
            challenge_class = CHALLENGE_CLASSES.get(class_id)
            response[challenge_class.id] = {
                "id": challenge_class.id,
                "name": challenge_class.name,
                "templates": challenge_class.templates,
                "scripts": challenge_class.scripts,
                "create": render_template(
                    challenge_class.templates["create"].lstrip("/")
                ),
            }

        return {"success": True, "data": response}
    ## flag saving
    @app.route('/userchallenge/api/challenges/<challenge_id>/flags',methods=['GET'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def flagget(challenge_id):
        flags = Flags.query.filter_by(challenge_id=challenge_id).all()
        schema = FlagSchema(many=True)
        response = schema.dump(flags)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    
    ## flag posting
    @app.route('/userchallenge/api/flags',methods=['POST'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def flagpost():
        req = request.get_json()
        schema = FlagSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/flags/types',methods=['GET'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def flagTypeGet():
        response = {}
        for class_id in FLAG_CLASSES:
            flag_class = FLAG_CLASSES.get(class_id)
            response[class_id] = {
                "name": flag_class.name,
                "templates": flag_class.templates,
            }
        return {"success": True, "data": response}
    @app.route('/userchallenge/api/flags/<flag_id>',methods=['GET'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def flagIDget(flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        response = schema.dump(flag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        response.data["templates"] = get_flag_class(flag.type).templates

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/flags/<flag_id>',methods=['PATCH'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def flagIDpatch(flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()
        schema = FlagSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=flag, partial=True)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/flags/<flag_id>',methods=['DELETE'])
    @userChallenge_allowed
    @authed_only
    #@userChallenge_allowed
    def flagIDdelete(flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()

        db.session.delete(flag)
        db.session.commit()
        db.session.close()

        return {"success": True}


    