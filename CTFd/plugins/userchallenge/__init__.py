from CTFd.api.v1.comments import get_comment_model
from CTFd.api.v1.helpers.request import validate_args
from CTFd.constants import RawEnum
from CTFd.schemas.comments import CommentSchema
from CTFd.schemas.files import FileSchema
from CTFd.schemas.hints import HintSchema
from CTFd.schemas.topics import ChallengeTopicSchema, TopicSchema
from CTFd.utils.decorators.visibility import check_challenge_visibility
from CTFd.utils.helpers.models import build_model_filters
from CTFd.utils.security.signing import serialize
from flask import render_template,request,Blueprint, url_for, abort,redirect,session
from sqlalchemy.sql import and_
from pathlib import Path
from CTFd.utils.plugins import override_template
from CTFd.plugins.challenges import CHALLENGE_CLASSES, get_chal_class
from CTFd.plugins.flags import FLAG_CLASSES,get_flag_class
from CTFd.utils.user import get_current_user, get_user_attrs,is_admin, authed,get_current_team
from CTFd.utils import set_config, user as current_user
from CTFd.models import ChallengeTopics, Challenges, Comments, Fails, Files, Solves, Flags, Tags, Topics, Users, db, Configs,Hints,HintUnlocks,Flags,Submissions
from CTFd.models import ChallengeFiles as ChallengeFilesModel
from CTFd.models import ChallengeTopics as ChallengeTopicsModel


from CTFd.utils.decorators import admins_only, during_ctf_time_only, require_verified_emails
from CTFd.schemas.flags import FlagSchema
from CTFd.schemas.tags import TagSchema
from CTFd.schemas.challenges import ChallengeSchema
from CTFd.cache import clear_challenges,clear_standings
from CTFd.utils import config, get_config, uploads
from CTFd.utils.dates import ctf_ended, ctf_paused, ctftime
from CTFd.utils.logging import log
from CTFd.utils.challenges import (
    get_solve_counts_for_challenges,
    get_solve_ids_for_user_id,
)
from CTFd.utils.config.visibility import (
    accounts_visible,
    challenges_visible,
    scores_visible
)
import functools

from flask_restx import Namespace


userChallenge = Blueprint('userchallenge',__name__,template_folder='templates',static_folder ='staticAssets')

class UserChallenges(db.Model):
    __tablename__ = "UserChallenges"
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer,db.ForeignKey('users.id'))
    challenge = db.Column(db.Integer,db.ForeignKey('challenges.id'))


    def __init__(self,user,challenge):
        self.user = user
        self.challenge = challenge

class UserChallenge:
    def __init__(self,id,name,category,author,value,type):
        self.id = id
        self.name = name
        self.category = category
        self.author = author
        self.value = value
        self.type = type

def add_User_Link(challenge_id):
    userchallenge = UserChallenges(get_current_user().id,challenge_id)
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


def load(app):

    app.db.create_all()

    app.register_blueprint(userChallenge,url_prefix='/userchallenge')

    # add config value false for allowing user challenges if not existent on startup
    if not Configs.query.filter_by(key="allowUserChallenges").first():
        conf = Configs(key="allowUserChallenges",value="false")
        db.session.add(conf)
        db.session.commit()

    registerTemplate('users/private.html','newUserPage.html')
    registerTemplate('admin/challenges/challenge.html','adminChallenge.html')
    

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
    
    @admins_only
    def challenges_listing():
        q = request.args.get("q")
        field = request.args.get("field")
        filters = []

        if q:
            # The field exists as an exposed column
            if Challenges.__mapper__.has_property(field):
                filters.append(getattr(Challenges, field).like("%{}%".format(q)))

        query = Challenges.query.filter(*filters).order_by(Challenges.id.asc())
        challenges_pre = query.all()
        total = query.count()

        challenges = []
        for n in challenges_pre:
            author = getUserForChallenge(n.id)
            challenges.append(UserChallenge(n.id,n.name,n.category,author,n.value,n.type))
            

        return render_template(
            "adminChallenges.html",
            challenges=challenges,
            total=total,
            q=q,
            field=field,)

    app.view_functions['admin.challenges_listing'] = challenges_listing


    @app.route('/userchallenge/api/config',methods=['GET','POST'])
    @admins_only
    def getConfig():
        newstate = update_allow_challenges()
        data = "disabled"
        if newstate:
            data = "enabled"
        return {"success":True,"data":data}

    @app.route('/userchallenge/challenges',methods=['GET','POST'])
    @userChallenge_allowed
    def view_challenges():
        #TODO: add custom html extension of admin/challenges/challenges
        #      change methods to check for rights and only display challenges by user
        #      add custom html to change challenge editing to be available to users
        #
        #      add other plugin to modify challenge creation?                    

        q = request.args.get("q")
        field = request.args.get("field") 
        challenges = getAllUserChallenges(q, field)
        total = len(challenges)    

        #return render_template('userChallenges.html',challenges=challenges,total=total,q=q,field=field)
        return render_template('userChallenges.html',challenges=challenges,total = total,q=q,field=field)    
    
    
    @app.route('/userchallenge/challenges/new',methods=['GET'])
    @userChallenge_allowed
    def view_newChallenge():
        types = CHALLENGE_CLASSES.keys()
        return render_template('createUserChallenge.html',types=types)
    
    @app.route('/userchallenge/challenges/<int:challenge_id>',methods=['GET'])
    @owned_by_user
    @userChallenge_allowed
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
    @app.route('/userchallenge/api/challenges/',methods=['POST'])
    @userChallenge_allowed
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
    @app.route('/userchallenge/api/challenges/',methods=['GET'])
    def getChallenges():

        # Get a cached mapping of challenge_id to solve_count
        solve_counts = get_solve_counts_for_challenges(admin=True)

        # Get list of solve_ids for current user
        if authed():
            user = get_current_user()
            user_solves = get_solve_ids_for_user_id(user_id=user.id)
        else:
            user_solves = set()

        # Aggregate the query results into the hashes defined at the top of
        # this block for later use
        if scores_visible() and accounts_visible():
            solve_count_dfl = 0
        else:
            # Empty out the solves_count if we're hiding scores/accounts
            solve_counts = {}
            # This is necessary to match the challenge detail API which returns
            # `None` for the solve count if visiblity checks fail
            solve_count_dfl = None

        chal_q = getAllUserChallenges(False,False)

        # Iterate through the list of challenges, adding to the object which
        # will be JSONified back to the client
        response = []
        tag_schema = TagSchema(view="user", many=True)

        # Gather all challenge IDs so that we can determine invalid challenge prereqs
        all_challenge_ids = {
            c.id for c in Challenges.query.with_entities(Challenges.id).all()
        }
        for challenge in chal_q:
            if challenge.requirements:
                requirements = challenge.requirements.get("prerequisites", [])
                anonymize = challenge.requirements.get("anonymize")
                prereqs = set(requirements).intersection(all_challenge_ids)
                if user_solves >= prereqs or admin_view:
                    pass
                else:
                    if anonymize:
                        response.append(
                            {
                                "id": challenge.id,
                                "type": "hidden",
                                "name": "???",
                                "value": 0,
                                "solves": None,
                                "solved_by_me": False,
                                "category": "???",
                                "tags": [],
                                "template": "",
                                "script": "",
                            }
                        )
                    # Fallthrough to continue
                    continue

            try:
                challenge_type = get_chal_class(challenge.type)
            except KeyError:
                # Challenge type does not exist. Fall through to next challenge.
                continue

            # Challenge passes all checks, add it to response
            response.append(
                {
                    "id": challenge.id,
                    "type": challenge_type.name,
                    "name": challenge.name,
                    "value": challenge.value,
                    "solves": solve_counts.get(challenge.id, solve_count_dfl),
                    "solved_by_me": challenge.id in user_solves,
                    "category": challenge.category,
                    "tags": tag_schema.dump(challenge.tags).data,
                    "template": challenge_type.templates["view"],
                    "script": challenge_type.scripts["view"],
                }
            )

        db.session.close()
        return {"success": True, "data": response}

    ## singular challenge
    @app.route('/userchallenge/api/challenges/<challenge_id>',methods=['PATCH'])
    @userChallenge_allowed
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
    @app.route('/userchallenge/api/challenges/<challenge_id>',methods=['DELETE'])
    @admins_only
    def delete(challenge_id):
        #delete UserChallenge reference
        query = UserChallenges.query.filter_by(challenge=challenge_id)
        userchal = query.first()
        if userchal:
            query.delete()
            db.session.commit()

        #delete challenge
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        chal_class = get_chal_class(challenge.type)
        chal_class.delete(challenge)


        clear_standings()
        clear_challenges()

        return {"success": True}
    
    @app.route('/userchallenge/challenges/preview/<challenge_id>')
    @userChallenge_allowed
    def render_preview(challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        chal_class = get_chal_class(challenge.type)
        user = get_current_user()
        team = get_current_team()

        files = []
        for f in challenge.files:
            token = {
                "user_id": user.id,
                "team_id": team.id if team else None,
                "file_id": f.id,
            }
            files.append(url_for("views.files", path=f.location, token=serialize(token)))

        tags = [
            tag["value"] for tag in TagSchema("user", many=True).dump(challenge.tags).data
        ]

        content = render_template(
            chal_class.templates["view"].lstrip("/"),
            solves=None,
            solved_by_me=False,
            files=files,
            tags=tags,
            hints=challenge.hints,
            max_attempts=challenge.max_attempts,
            attempts=0,
            challenge=challenge,
        )
        return render_template(
            "userPreview.html", content=content, challenge=challenge
        )
    
    ## FLAGS
    @app.route('/userchallenge/api/challenges/types')
    @userChallenge_allowed
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
                    challenge_class.templates["create"].lstrip("admin/challenges/")
                ),
            }

        return {"success": True, "data": response}
    ## flag saving
    @app.route('/userchallenge/api/challenges/<challenge_id>/flags',methods=['GET'])
    @userChallenge_allowed
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
    def flagIDdelete(flag_id):
        flag = Flags.query.filter_by(id=flag_id).first_or_404()

        db.session.delete(flag)
        db.session.commit()
        db.session.close()

        return {"success": True}

    #FILES
    @app.route('/userchallenge/api/challenges/<challenge_id>/files', methods=['GET'])
    @userChallenge_allowed
    def getchallengeFiles(challenge_id):
        response = []

        challenge_files = ChallengeFilesModel.query.filter_by(
            challenge_id=challenge_id
        ).all()

        for f in challenge_files:
            response.append({"id": f.id, "type": f.type, "location": f.location})
        return {"success": True, "data": response}
    files_namespace = Namespace("files", description="Endpoint to retrieve Files")
    @app.route('/userchallenge/api/files',methods=['POST'])
    @files_namespace.doc(
        description="Endpoint to get file objects in bulk",
        responses={
            200: ("Success", "FileDetailedSuccessResponse"),
            400: (
                "An error occured processing the provided or stored data",
                "APISimpleErrorResponse",
            ),
        },
        params={
            "file": {
                "in": "formData",
                "type": "file",
                "required": True,
                "description": "The file to upload",
            }
        },
    )
    @validate_args(
        {
            "challenge_id": (int, None),
            "challenge": (int, None),
            "page_id": (int, None),
            "page": (int, None),
            "type": (str, None),
            "location": (str, None),
        },
        location="form",
    )
    @userChallenge_allowed
    def uploadFile(form_args):
        files = request.files.getlist("file")
        location = form_args.get("location")
        # challenge_id
        # page_id

        # Handle situation where users attempt to upload multiple files with a single location
        if len(files) > 1 and location:
            return {
                "success": False,
                "errors": {
                    "location": ["Location cannot be specified with multiple files"]
                },
            }, 400

        objs = []
        for f in files:
            # uploads.upload_file(file=f, chalid=req.get('challenge'))
            try:
                obj = uploads.upload_file(file=f, **form_args)
            except ValueError as e:
                return {
                    "success": False,
                    "errors": {"location": [str(e)]},
                }, 400
            objs.append(obj)

        schema = FileSchema(many=True)
        response = schema.dump(objs)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/files/<file_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteFile(file_id):
        f = Files.query.filter_by(id=file_id).first_or_404()

        uploads.delete_file(file_id=f.id)
        db.session.delete(f)
        db.session.commit()
        db.session.close()

        return {"success": True}
    @app.route('/userchallenge/api/files/<file_id>',methods=['GET'])
    @userChallenge_allowed
    def getFile(file_id):
        f = Files.query.filter_by(id=file_id).first_or_404()
        schema = FileSchema()
        response = schema.dump(f)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}

    #TOPICS
    @app.route('/userchallenge/api/challenges/<challenge_id>/topics', methods=['GET'])
    @userChallenge_allowed
    def getTopics(challenge_id):
        response = []

        topics = ChallengeTopicsModel.query.filter_by(challenge_id=challenge_id).all()

        for t in topics:
            response.append(
                {
                    "id": t.id,
                    "challenge_id": t.challenge_id,
                    "topic_id": t.topic_id,
                    "value": t.topic.value,
                }
            )
        return {"success": True, "data": response}
    
    @app.route('/userchallenge/api/topics',methods=['POST'])
    @userChallenge_allowed
    def createTopic():
        req = request.get_json()
        value = req.get("value")

        if value:
            topic = Topics.query.filter_by(value=value).first()
            if topic is None:
                schema = TopicSchema()
                response = schema.load(req, session=db.session)

                if response.errors:
                    return {"success": False, "errors": response.errors}, 400

                topic = response.data
                db.session.add(topic)
                db.session.commit()
        else:
            topic_id = req.get("topic_id")
            topic = Topics.query.filter_by(id=topic_id).first_or_404()

        req["topic_id"] = topic.id
        topic_type = req.get("type")
        if topic_type == "challenge":
            schema = ChallengeTopicSchema()
            response = schema.load(req, session=db.session)
        else:
            return {"success": False}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}

    @app.route('/userchallenge/api/topics',methods=['DELETE'])
    @validate_args(
        {"type": (str, None), "target_id": (int, 0)},
        location="query",
    )
    def deleteTop(query_args):
        topic_type = query_args.get("type")
        target_id = int(query_args.get("target_id", 0))

        if topic_type == "challenge":
            Model = ChallengeTopics
        else:
            return {"success": False}, 400

        topic = Model.query.filter_by(id=target_id).first_or_404()
        db.session.delete(topic)
        db.session.commit()
        db.session.close()

        return {"success": True}
    @app.route('/userchallenge/api/topics/<topic_id>',methods=['GET'])
    @userChallenge_allowed
    def getTopic(topic_id):
        topic = Topics.query.filter_by(id=topic_id).first_or_404()
        response = TopicSchema().dump(topic)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/topic/<topic_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteTopic(topic_id):
        topic = Topics.query.filter_by(id=topic_id).first_or_404()
        db.session.delete(topic)
        db.session.commit()
        db.session.close()

        return {"success": True}
    
    # TAGS
    @app.route('/userchallenge/api/challenges/<challenge_id>/tags',methods=['GET'])
    @userChallenge_allowed
    def getTags(challenge_id):
        response = []

        tags = Tags.query.filter_by(challenge_id=challenge_id).all()

        for t in tags:
            response.append(
                {"id": t.id, "challenge_id": t.challenge_id, "value": t.value}
            )
        return {"success": True, "data": response}

    @app.route('/userchallenge/api/tags',methods=['POST'])
    @userChallenge_allowed
    def createTag():
        req = request.get_json()
        schema = TagSchema()
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/tags/<tag_id>',methods=['GET'])
    @userChallenge_allowed
    def getTag(tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()

        response = TagSchema().dump(tag)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/tags/<tag_id>',methods=['PATCH'])
    @userChallenge_allowed
    def patchTag(tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        schema = TagSchema()
        req = request.get_json()

        response = schema.load(req, session=db.session, instance=tag)
        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.commit()

        response = schema.dump(response.data)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/tags/<tag_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteTag(tag_id):
        tag = Tags.query.filter_by(id=tag_id).first_or_404()
        db.session.delete(tag)
        db.session.commit()
        db.session.close()

        return {"success": True}

    # Hints
    @app.route('/userchallenge/api/challenges/<challenge_id>/hints',methods=['GET'])
    @userChallenge_allowed
    def getHints(challenge_id):
        hints = Hints.query.filter_by(challenge_id=challenge_id).all()
        schema = HintSchema(many=True)
        response = schema.dump(hints)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/hints',methods=['POST'])
    @userChallenge_allowed
    def createHint():
        req = request.get_json()
        schema = HintSchema(view="admin")
        response = schema.load(req, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/hints/<hint_id>',methods=['GET'])
    @userChallenge_allowed
    def getHint(hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        user = get_current_user()

        # We allow public accessing of hints if challenges are visible and there is no cost or prerequisites
        # If there is a cost or a prereq we should block the user from seeing the hint
        if user is None:
            if hint.cost or hint.prerequisites:
                return (
                    {
                        "success": False,
                        "errors": {"cost": ["You must login to unlock this hint"]},
                    },
                    403,
                )

        if hint.prerequisites:
            requirements = hint.prerequisites

            # Get the IDs of all hints that the user has unlocked
            all_unlocks = HintUnlocks.query.filter_by(account_id=user.account_id).all()
            unlock_ids = {unlock.target for unlock in all_unlocks}

            # Get the IDs of all free hints
            free_hints = Hints.query.filter_by(cost=0).all()
            free_ids = {h.id for h in free_hints}

            # Add free hints to unlocked IDs
            unlock_ids.update(free_ids)

            # Filter out hint IDs that don't exist
            all_hint_ids = {h.id for h in Hints.query.with_entities(Hints.id).all()}
            prereqs = set(requirements).intersection(all_hint_ids)

            # If the user has the necessary unlocks or is admin we should allow them to view
            if unlock_ids >= prereqs or is_admin():
                pass
            else:
                return (
                    {
                        "success": False,
                        "errors": {
                            "requirements": [
                                "You must unlock other hints before accessing this hint"
                            ]
                        },
                    },
                    403,
                )

        view = "unlocked"
        if hint.cost:
            view = "locked"
            unlocked = HintUnlocks.query.filter_by(
                account_id=user.account_id, target=hint.id
            ).first()
            if unlocked:
                view = "unlocked"

        if is_admin():
            if request.args.get("preview", False):
                view = "admin"

        response = HintSchema(view=view).dump(hint)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/hints/<hint_id>',methods=['PATCH'])
    @userChallenge_allowed
    def patchHint(hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        req = request.get_json()

        schema = HintSchema(view="admin")
        response = schema.load(req, instance=hint, partial=True, session=db.session)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        db.session.add(response.data)
        db.session.commit()

        response = schema.dump(response.data)

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/hints/<hint_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteHint(hint_id):
        hint = Hints.query.filter_by(id=hint_id).first_or_404()
        db.session.delete(hint)
        db.session.commit()
        db.session.close()

        return {"success": True}

    # Requirements
    @app.route('/userchallenge/api/challenges/<challenge_id>/requirements',methods=['GET'])
    @userChallenge_allowed
    def getReqs(challenge_id):
        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
        return {"success": True, "data": challenge.requirements}

    # Comments
    @app.route('/userchallenge/api/comments',methods=['GET'])
    @userChallenge_allowed
    @validate_args(
        {
            "challenge_id": (int, None),
            "user_id": (int, None),
            "team_id": (int, None),
            "page_id": (int, None),
            "q": (str, None),
            "field": (RawEnum("CommentFields", {"content": "content"}), None),
        },
        location="query",
    )
    def getComs(query_args):
        q = query_args.pop("q", None)
        field = str(query_args.pop("field", None))
        CommentModel = get_comment_model(data=query_args)
        filters = build_model_filters(model=CommentModel, query=q, field=field)

        comments = (
            CommentModel.query.filter_by(**query_args)
            .filter(*filters)
            .order_by(CommentModel.id.desc())
            .paginate(max_per_page=100, error_out=False)
        )
        schema = CommentSchema(many=True)
        response = schema.dump(comments.items)

        if response.errors:
            return {"success": False, "errors": response.errors}, 400

        return {
            "meta": {
                "pagination": {
                    "page": comments.page,
                    "next": comments.next_num,
                    "prev": comments.prev_num,
                    "pages": comments.pages,
                    "per_page": comments.per_page,
                    "total": comments.total,
                }
            },
            "success": True,
            "data": response.data,
        }
    @app.route('/userchallenge/api/comments',methods=['POST'])
    @userChallenge_allowed
    @validate_args(
        {
            "challenge_id": (int, None),
            "user_id": (int, None),
            "team_id": (int, None),
            "page_id": (int, None),
            "q": (str, None),
            "field": (RawEnum("CommentFields", {"content": "content"}), None),
        },
        location="query",
    )
    def postCom(query_args):
        req = request.get_json()
        # Always force author IDs to be the actual user
        req["author_id"] = session["id"]
        CommentModel = get_comment_model(data=req)

        m = CommentModel(**req)
        db.session.add(m)
        db.session.commit()

        schema = CommentSchema()

        response = schema.dump(m)
        db.session.close()

        return {"success": True, "data": response.data}
    @app.route('/userchallenge/api/comments/<comment_id>',methods=['DELETE'])
    @userChallenge_allowed
    def deleteCom(comment_id):
        comment = Comments.query.filter_by(id=comment_id).first_or_404()
        if comment.author_id == get_current_user().id or is_admin():
            db.session.delete(comment)
            db.session.commit()
            db.session.close()        
            return {"success": True}
        else:
            return {"success": False}
    
    def challengeAttempt():

        if authed() is False:
            return {"success": True, "data": {"status": "authentication_required"}}, 403

        if not request.is_json:
            request_data = request.form
        else:
            request_data = request.get_json()

        challenge_id = request_data.get("challenge_id")

        non_admin = non_admin_preview(challenge_id)
        if(non_admin):
            return non_admin
        
        return challengeAttemptDefault(challenge_id,request_data)

    @userChallenge_allowed
    def non_admin_preview(challenge_id):
        preview = request.args.get("preview", False)
        if preview:
            challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
            chal_class = get_chal_class(challenge.type)
            status, message = chal_class.attempt(challenge, request)

            return {
                "success": True,
                "data": {
                    "status": "correct" if status else "incorrect",
                    "message": message,
                },
            }

    @check_challenge_visibility
    @during_ctf_time_only
    @require_verified_emails
    def challengeAttemptDefault( challenge_id,request_data):
        if current_user.is_admin():
            preview = request.args.get("preview", False)
            if preview:
                challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()
                chal_class = get_chal_class(challenge.type)
                status, message = chal_class.attempt(challenge, request)

                return {
                    "success": True,
                    "data": {
                        "status": "correct" if status else "incorrect",
                        "message": message,
                    },
                }

        if ctf_paused():
            return (
                {
                    "success": True,
                    "data": {
                        "status": "paused",
                        "message": "{} is paused".format(config.ctf_name()),
                    },
                },
                403,
            )

        user = get_current_user()
        team = get_current_team()

        # TODO: Convert this into a re-useable decorator
        if config.is_teams_mode() and team is None:
            abort(403)

        fails = Fails.query.filter_by(
            account_id=user.account_id, challenge_id=challenge_id
        ).count()

        challenge = Challenges.query.filter_by(id=challenge_id).first_or_404()

        if challenge.state == "hidden":
            abort(404)

        if challenge.state == "locked":
            abort(403)

        if challenge.requirements:
            requirements = challenge.requirements.get("prerequisites", [])
            solve_ids = (
                Solves.query.with_entities(Solves.challenge_id)
                .filter_by(account_id=user.account_id)
                .order_by(Solves.challenge_id.asc())
                .all()
            )
            solve_ids = {solve_id for solve_id, in solve_ids}
            # Gather all challenge IDs so that we can determine invalid challenge prereqs
            all_challenge_ids = {
                c.id for c in Challenges.query.with_entities(Challenges.id).all()
            }
            prereqs = set(requirements).intersection(all_challenge_ids)
            if solve_ids >= prereqs:
                pass
            else:
                abort(403)

        chal_class = get_chal_class(challenge.type)

        # Anti-bruteforce / submitting Flags too quickly
        kpm = current_user.get_wrong_submissions_per_minute(user.account_id)
        kpm_limit = int(get_config("incorrect_submissions_per_min", default=10))
        if kpm > kpm_limit:
            if ctftime():
                chal_class.fail(
                    user=user, team=team, challenge=challenge, request=request
                )
            log(
                "submissions",
                "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [TOO FAST]",
                name=user.name,
                submission=request_data.get("submission", "").encode("utf-8"),
                challenge_id=challenge_id,
                kpm=kpm,
            )
            # Submitting too fast
            return (
                {
                    "success": True,
                    "data": {
                        "status": "ratelimited",
                        "message": "You're submitting flags too fast. Slow down.",
                    },
                },
                429,
            )

        solves = Solves.query.filter_by(
            account_id=user.account_id, challenge_id=challenge_id
        ).first()

        # Challenge not solved yet
        if not solves:
            # Hit max attempts
            max_tries = challenge.max_attempts
            if max_tries and fails >= max_tries > 0:
                return (
                    {
                        "success": True,
                        "data": {
                            "status": "incorrect",
                            "message": "You have 0 tries remaining",
                        },
                    },
                    403,
                )

            status, message = chal_class.attempt(challenge, request)
            if status:  # The challenge plugin says the input is right
                if ctftime() or current_user.is_admin():
                    chal_class.solve(
                        user=user, team=team, challenge=challenge, request=request
                    )
                    clear_standings()
                    clear_challenges()

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [CORRECT]",
                    name=user.name,
                    submission=request_data.get("submission", "").encode("utf-8"),
                    challenge_id=challenge_id,
                    kpm=kpm,
                )
                return {
                    "success": True,
                    "data": {"status": "correct", "message": message},
                }
            else:  # The challenge plugin says the input is wrong
                if ctftime() or current_user.is_admin():
                    chal_class.fail(
                        user=user, team=team, challenge=challenge, request=request
                    )
                    clear_standings()
                    clear_challenges()

                log(
                    "submissions",
                    "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [WRONG]",
                    name=user.name,
                    submission=request_data.get("submission", "").encode("utf-8"),
                    challenge_id=challenge_id,
                    kpm=kpm,
                )

                if max_tries:
                    # Off by one since fails has changed since it was gotten
                    attempts_left = max_tries - fails - 1
                    tries_str = pluralize(attempts_left, singular="try", plural="tries")
                    # Add a punctuation mark if there isn't one
                    if message[-1] not in "!().;?[]{}":
                        message = message + "."
                    return {
                        "success": True,
                        "data": {
                            "status": "incorrect",
                            "message": "{} You have {} {} remaining.".format(
                                message, attempts_left, tries_str
                            ),
                        },
                    }
                else:
                    return {
                        "success": True,
                        "data": {"status": "incorrect", "message": message},
                    }
        # Challenge already solved
        else:
            log(
                "submissions",
                "[{date}] {name} submitted {submission} on {challenge_id} with kpm {kpm} [ALREADY SOLVED]",
                name=user.name,
                submission=request_data.get("submission", "").encode("utf-8"),
                challenge_id=challenge_id,
                kpm=kpm,
            )
            return {
                "success": True,
                "data": {
                    "status": "already_solved",
                    "message": "You already solved this",
                },
            }
        
    app.view_functions['api.challenges_challenge_attempt'] = challengeAttempt
    