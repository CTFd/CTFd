from flask import Blueprint
from flask_restx import Namespace, Resource

from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES
from CTFd.plugins import register_plugin_assets_directory
import importlib

print("photo_challenges: module imported")

from .models import PhotoSubmission
from CTFd.plugins.migrations import upgrade
from CTFd.api import CTFd_API_v1

from CTFd.models import (
    ChallengeFiles,
    Challenges,
    Fails,
    Flags,
    Hints,
    Solves,
    Tags,
    db,
    Awards,
)
from CTFd.utils.logging import log

# class SubflagChallengeType(BaseChallenge):

#     # overrides the default function to create a challenge
#     @classmethod
#     def create(cls, request):
#         """
#         This method is used to process the challenge creation request.

#         :param request:
#         :return:
#         """
#         # input data
#         data = request.form or request.get_json()

#         # get list with only challenge information (no information about subflags and their hints)
#         challenge_data = {key:value for (key,value) in data.items() if not key.startswith('subflag')}

#         # create new Subflag challenge with all ordinary challenge information (excluding subflag data)
#         challenge = SubflagChallenge(**challenge_data)
#         db.session.add(challenge)
#         db.session.commit()

#         # get list with only subflag information 
#         subflag_data = {key:value for (key,value) in data.items() if key.startswith('subflag')}
        
#         # creates an array to save the subflag information in
#         subflag_data_list = []

#         # the number of attributes associated with each subflag
#         num_items = 6

#         # tranfers the subflag data to a array
#         for key in subflag_data:
#             subflag_data_list.append(subflag_data[key])

#         # iterates over the array taking into consideration the number of attributes each subflag has
#         for num in range(int(len(subflag_data_list) / num_items)):
#             # if the subflag has an empty field dont create it
#             if (len(subflag_data_list[num_items*num]) == 0 or len(subflag_data_list[num_items*num+3]) == 0) or subflag_data_list[num_items*num+4] is None:
#                 break
#             else:
#                 # if all fields are filled out create a subflag
#                 subflag = Subflags(
#                     challenge_id = challenge.id,
#                     subflag_name = subflag_data_list[num_items*num],
#                     subflag_desc = subflag_data_list[num_items*num+1],
#                     subflag_placeholder = subflag_data_list[num_items*num+2],
#                     subflag_key = subflag_data_list[num_items*num+3],
#                     subflag_order = subflag_data_list[num_items*num+4],
#                     subflag_points = subflag_data_list[num_items*num+5]
#                 )
#                 db.session.add(subflag)
#                 db.session.commit()        
#         return challenge

#     # override the default function to delete a challenge
#     @classmethod
#     def delete(cls, challenge):
#         """
#         This method is used to delete the resources used by a challenge.
#         :param challenge:
#         :return:
#         """
#         # gets a list of all subflags associated to the challenge
#         subflags = Subflags.query.filter_by(challenge_id = challenge.id).all()
#         for subflag in subflags:
#             # deletes all solves and hints associated with the subflag
#             SubflagSolve.query.filter_by(subflag_id = subflag.id).delete()
#             SubflagHint.query.filter_by(subflag_id = subflag.id).delete()

#         # delete all subflags of the challenge
#         Subflags.query.filter_by(challenge_id=challenge.id).delete()

#         # delete all ordinary challenge files
#         Fails.query.filter_by(challenge_id=challenge.id).delete()
#         Solves.query.filter_by(challenge_id=challenge.id).delete()
#         Flags.query.filter_by(challenge_id=challenge.id).delete()
#         files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
#         for f in files:
#             delete_file(f.id)
#         ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
#         Tags.query.filter_by(challenge_id=challenge.id).delete()
#         Hints.query.filter_by(challenge_id=challenge.id).delete()
#         SubflagChallenge.query.filter_by(id=challenge.id).delete()
#         Challenges.query.filter_by(id=challenge.id).delete()
#         db.session.commit()

photo_namespace = Namespace("photos", description="Endpoint to handle photo evidence submissions")

class PhotoChallengeModel(Challenges):
    __mapper_args__ = {"polymorphic_identity": "photo"}
    id = db.Column(db.Integer, 
        db.ForeignKey("challenges.id", ondelete="CASCADE"), 
        primary_key=True)

class PhotoChallengeType(BaseChallenge):
    # Use the short type identifier `photo` to match values stored in the
    # `challenges.type` column (CTFd expects challenge.type to match the
    # registered challenge class id).
    id = "photo"
    name = "Photo Challenge"
    templates = {
        "create": "/plugins/photo_challenges/assets/create.html",
        "update": "/plugins/photo_challenges/assets/update.html",
        "view": "/plugins/photo_challenges/assets/view.html",
    }
    scripts = {
        "create": "/plugins/photo_challenges/assets/create.js",
        "update": "/plugins/photo_challenges/assets/update.js",
        "view": "/plugins/photo_challenges/assets/view.js"
    }
    route = "/plugins/photo_challenges/assets"
    blueprint = Blueprint(
        "photo_challenges", __name__,
        template_folder="templates",
        static_folder="assets"
    )
    challenge_model = PhotoChallengeModel # Use default Challenges table

    @classmethod
    def attempt(cls, challenge, request):
        """
        This method is used to check whether a given input is right or wrong.
        Since photo challenges require manual review, we always return False here.
        However, we can set the submission to a "pending review" status.
        ...
             Parameters
                ----------
                challenge : Challenge
                    The Challenge object from the database
                submission : request
                    The submitted request by player

            Returns
                -------
                (boolean, String)
                    (is flag correct, message to show)
        """
        data = request.form or request.get_json()
        provided = data.get("submission", "").strip()
        
        # Log incoming request metadata for debugging
        print("Photo Challenge Attempt: Logging request metadata")
        print("Content-Type:", request.content_type)
        print("Headers:", request.headers)
        try:
            print(f"[photo] attempt called: content_type={request.content_type} headers={request.headers.get('Content-Type')}")
            keys = ",".join(list(request.files.keys()))
            print(f"[photo] request.files keys: {keys}")
            # Log uploaded filenames (do not log file content)
            for k in request.files:
                f = request.files[k]
                print(f"[photo] uploaded file field={k} filename={getattr(f, 'filename', None)}")
            print(f"[photo] request.form keys: {','.join(list(request.form.keys()))}")
        except Exception as e:
            print(f"[photo] error logging request: {str(e)}")

        # We DO NOT accept flags — require an uploaded file
        if "file" not in request.files:
            return False, "No photo uploaded"

        photo = request.files["file"]
        if not photo or photo.filename == "":
            return False, "Invalid photo"

        # Save photo somewhere (plugin `routes.py` currently handles uploads for review)
        # Mark submission as pending (NOT solved)
        return False, "Photo submitted for review"

    @classmethod
    def delete(cls, challenge):
        """
        This method is used to delete the resources used by a challenge.
        :param challenge:
        :return:
        """
        # Delete all photo submissions associated with the challenge
        PhotoSubmission.query.filter_by(challenge_id=challenge.id).delete()

        # Call base class delete to remove standard challenge resources
        super().delete(challenge)

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the challenge with new information.
        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        for key, value in data.items():
            if hasattr(challenge, key):
                setattr(challenge, key, value)

        db.session.commit()
        return challenge


# from CTFd.utils.uploads import delete_file #to delete challenge files
# from CTFd.utils.decorators import admins_only, authed_only
# from CTFd.plugins import register_plugin_assets_directory
# from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
# from CTFd.utils.config import is_teams_mode
# from CTFd.utils.user import get_current_team, get_current_user
# from datetime import datetime



# # database model for the individual subflag
# # includes: id, reference to the associated challenge, desc, key (solution), order
# class Subflags(db.Model):
#     id = db.Column(db.Integer, primary_key = True)
#     challenge_id = db.Column(db.Integer, 
#         db.ForeignKey("challenges.id", ondelete="CASCADE"))
#     subflag_name = db.Column(db.String(128))
#     subflag_desc = db.Column(db.String(128))
#     subflag_placeholder = db.Column(db.String(128))
#     subflag_key = db.Column(db.String(128))
#     subflag_order = db.Column(db.Integer)
#     subflag_points = db.Column(db.Integer)


#     def __init__(self, challenge_id, subflag_name, subflag_desc, subflag_placeholder, subflag_key, subflag_order, subflag_points):
#         self.challenge_id = challenge_id
#         self.subflag_name = subflag_name
#         self.subflag_desc = subflag_desc
#         self.subflag_placeholder = subflag_placeholder
#         self.subflag_key = subflag_key
#         self.subflag_order = subflag_order
#         self.subflag_points = subflag_points


#describes the challenge type 


# API Extensions for Subflags

# endpoint to attach a subflag to a challenge
# inputs: challenge_id, subflag_desc, subflag_key, subflag_order


# @subflags_namespace.route("")
# class Subflag(Resource):
#     """
# 	The Purpose of this API Endpoint is to allow an admin to add a single subflag to a challenge
# 	"""
#     # user has to be authentificated as admin to call this endpoint    
#     @admins_only
#     def post(self):
#         # parses request arguements into data
#         if request.content_type != "application/json":
#             data = request.form
#         else:
#             data = request.get_json()

#         if (data["challenge_id"] and data["subflag_name"] and data["subflag_desc"] and data["subflag_key"] and data["subflag_points"]  and data["subflag_order"] is not None):
#             # creates new entry in Subflag table with the request arguments
#             subflag = Subflags(
#                 challenge_id = data["challenge_id"],
#                 challenge_name = data["challenge_name"],
#                 subflag_desc = data["subflag_desc"],
#                 subflag_placeholder = data["subflag_placeholder"],
#                 subflag_key = data["subflag_key"],
#                 subflag_order = data["subflag_order"],
#                 subflag_points = data["subflag_points"],
#             )                
#             db.session.add(subflag)
#             db.session.commit()
            
#             return {"success": True, "data": {"message": "New subflag created"}}
#         else:
#             return {"success": False, "data": {"message": "at least one input empty"}}

# @subflags_namespace.route("/<subflag_id>")
# class Subflag(Resource):
#     """
#     The Purpose of this API Endpoint is to allow an admin to update a single subflag
#     """
#     @admins_only
#     def patch(self, subflag_id):
#         # parse request arguments
#         data = request.get_json()
#         print(data)
#         # get subflag from database
#         subflag = Subflags.query.filter_by(id = subflag_id).first()

#         # update subflag data entries if the entry field are not empty 
#         if len(data["subflag_name"]) != 0:
#             subflag.subflag_name = data["subflag_name"]
#         if len(data["subflag_desc"]) != 0:
#             subflag.subflag_desc = data["subflag_desc"]   
#         if len(data["subflag_placeholder"]) != 0:
#             subflag.subflag_placeholder = data["subflag_placeholder"]        
#         if len(data["subflag_key"]) != 0:
#             subflag.subflag_key = data["subflag_key"]
#         number = int(data["subflag_order"])
#         if isinstance(number, int):
#             subflag.subflag_order = number

#         number2 = int(data["subflag_points"])
#         if isinstance(number2, int):
#             subflag.subflag_points = number2

#         db.session.add(subflag)
#         db.session.commit()

#         return {"success": True, "data": {"message": "sucessfully updated"}}


#     """
#     The Purpose of this API Endpoint is to allow admins to delete a subflag
#     """
#     # user has to be authentificated as admin to call this endpoint
#     @admins_only
#     def delete(self, subflag_id):

#         # delete associated hints, solved and the subflag itself
#         SubflagHint.query.filter_by(subflag_id = subflag_id).delete
#         SubflagSolve.query.filter_by(subflag_id = subflag_id).delete()
#         Subflags.query.filter_by(id = subflag_id).delete()

#         db.session.commit()

#         return {"success": True, "data": {"message": "Subflag deleted"}}

# @subflags_namespace.route("/challenges/<chal_id>/update")
# class Updates(Resource):
#     """
# 	The Purpose of this API Endpoint is to allow an admin to view the Subflags (including the key) in the upgrade screen
# 	"""
#     # user has to be authentificated as admin to call this endpoint
#     @admins_only
#     def get(self, chal_id):
#         # searches for all subflags connected to the challenge
#         subflag_data = Subflags.query.filter_by(challenge_id = chal_id).all()        
        
#         # return a json containng for each subflag: desc, key, order, hints
#         # where hints includes the id of all hints and the order they are supposed to be in
#         subflag_json = {}
#         for i in range(len(subflag_data)):
#             id_var = str(subflag_data[i].id)
#             hints = SubflagHint.query.filter_by(subflag_id = id_var).all()
#             subflag_json[id_var]  =  {
#                 "name": subflag_data[i].subflag_name,
#                 "desc": subflag_data[i].subflag_desc,
#                 "placeholder": subflag_data[i].subflag_placeholder,
#                 "key": subflag_data[i].subflag_key,
#                 "order": subflag_data[i].subflag_order,
#                 "points": subflag_data[i].subflag_points,
#                 "hints": {}
#             }
#             for it in range(len(hints)):
#                 subflag_json[id_var]["hints"][hints[it].id] = {"order": hints[it].hint_order}
#         return subflag_json

# class Hint(Resource):
#     """
#     The Purpose of this API Endpoint is to allow admins to attach a hint to a specific subflag
#     """
#     # user has to be authentificated as admin to call this endpoint
#     @admins_only
#     def post(self, hint_id):
#         #parse request arguements
#         data = request.get_json()

#         # creates new entry in subflag hint database
#         subflag_hint = SubflagHint(
#             id = hint_id,
#             subflag_id = data["subflag_id"],
#             hint_order = data["hint_order"],
#         )
#         db.session.add(subflag_hint)
#         db.session.commit()
#         return {"success": True, "data": {"message": "Hint attached"}}

# @subflags_namespace.route("/challenges/<chal_id>/view")
# class Views(Resource):
#     """
# 	The Purpose of this API Endpoint is to allow an user to see the subflags when solving a challenge. 
# 	"""
#     # user has to be authentificated to call this endpoint
#     @authed_only
#     def get(self, chal_id):
#         # parse challenge id from request arguments
#         id = request.args.get('id')
#         # get team id from the user that called the endpoint
#         team = get_current_team()
#         # searches for all subflags connected to the challenge
#         subflag_data = Subflags.query.filter_by(challenge_id = chal_id).all()

#         # return a json containg for each subflag: subflag_id, desc, order, whether the subflag has been solved by the users team, hints
#         # where hints includes the id of all hints and the order they are supposed to be in
#         subflag_json = {}
#         for i in range(len(subflag_data)):
#             id_var = str(subflag_data[i].id)
#             # bool whether the subflag has been solved by the current team
#             solved = SubflagSolve.query.filter_by(subflag_id = id_var, team_id = team.id).first() is not None
#             hints = SubflagHint.query.filter_by(subflag_id = id_var).all()
#             subflag_json[id_var]  =  {
#                 "desc": subflag_data[i].subflag_desc,
#                 "placeholder": subflag_data[i].subflag_placeholder,
#                 "order": subflag_data[i].subflag_order,
#                 "solved": solved,
#                 "points": subflag_data[i].subflag_points,
#                 "hints": {},
#             }            
#             for it in range(len(hints)):
#                 subflag_json[id_var]["hints"][hints[it].id] = {"order": hints[it].hint_order}
#         return subflag_json

# @subflags_namespace.route("/solve/<subflag_id>")
# class Solve(Resource):
#     """
# 	The Purpose of this API Endpoint is to allow an user to post a solve atempt. 
# 	"""
#     # user has to be authentificated to call this endpoint
#     @authed_only
#     def post(self, subflag_id):
#         # parse request arguements 
#         data = request.get_json()

#         # pulls the right key from the database
#         right_key = Subflags.query.filter_by(id = subflag_id).first()
        
#         # if the key is not right return an error message
#         if right_key.subflag_key != data["answer"]:
#             return {"success": True, "data": {"message": "False Attempt", "solved": False}}

#         #  if the challenge was already solved return a error message
#         team = get_current_team()
#         solved = SubflagSolve.query.filter_by(subflag_id = subflag_id, team_id = team.id).first() is not None
#         if solved:
#             print("Subflag: already solved")
#             return {"success": True, "data": {"message": "was already solved", "solved": True}}
        
#         # if the key is correct and the flag was not already solved
#         # add solve to database and return true
#         else:            
#             user = get_current_user()
            
#             # if team mode is enabled then save user and team in the database 
#             if is_teams_mode:
#                 solve = SubflagSolve(
#                     subflag_id =subflag_id,
#                     user_id = user.id,
#                     team_id = team.id,
#                 )
#                 award = Awards(
#                     name= Subflags.query.filter_by(id = subflag_id).all()[0].subflag_name,
#                     user_id = user.id,
#                     team_id = team.id,
#                     value = Subflags.query.filter_by(id = subflag_id).all()[0].subflag_points
#                 )
#             # if user mode save team id as user id to the database
#             else:
#                 solve = SubflagSolve(
#                     subflag_id=subflag_id,
#                     user_id=user.id,
#                     team_id=user.id,
#                 )
#                 award = Awards(
#                     name= Subflags.query.filter_by(id = subflag_id).all()[0].subflag_name,
#                     user_id=user.id,
#                     team_id=user.id,
#                     value = Subflags.query.filter_by(id = subflag_id).all()[0].subflag_points
#                 )
#             db.session.add(solve)
#             db.session.add(award)
#             db.session.commit()
#             return {"success": True, "data": {"message": "Subflag solved", "solved": True}}  
    
def load(app):
    app.logger.info("photo_challenges: load() starting")
    upgrade(plugin_name="photo_challenges")
    app.db.create_all()

    # # Register your blueprint routes
    app.register_blueprint(PhotoChallengeType.blueprint)

    CHALLENGE_CLASSES[PhotoChallengeType.id] = PhotoChallengeType

    # Register static folder so assets are accessible
    register_plugin_assets_directory(
        app,
        base_path="/plugins/photo_challenges/assets"
    )

    # Register API namespace so endpoints are available under `/api/v1/photo_challenges`.
    # Namespace registration may race with application/API initialization, so
    # defer registration until the app is fully initialized. Using
    # `before_first_request` ensures the RESTX API object exists and we avoid
    # ad-hoc `add_url_rule` hacks.
    def _register_namespaces():
        try:
            # Import namespace lazily to avoid import-time side effects
            from .routes import photo_namespace
            CTFd_API_v1.add_namespace(photo_namespace, '/photo_challenges')
            app.logger.info("photo_challenges: registered RESTX namespace /photo_challenges")
        except Exception:
            # If registration fails for any reason, silently ignore — the
            # plugin will still expose functionality via the blueprint
            # (static/templates) and a future request can surface errors.
            pass

    app.before_first_request(_register_namespaces)

    # As a robust fallback for cases where the RESTX namespace isn't
    # immediately available (due to app/plugin init ordering), also
    # register direct Flask URL rules that map to the Resource classes
    # defined in `routes.py`. This preserves canonical RESTX usage while
    # ensuring the endpoints remain reachable in all environments.
    # Register lightweight lazy wrappers for endpoints that would otherwise
    # import `routes.py` at plugin load time. Importing `routes.py` triggers
    # creation of a local `Api(...)` which can cause initialization hangs
    # in some environments. These wrappers import `routes` only when the
    # endpoint is actually invoked.
    def _lazy_view(func_name):
        def _view(*args, **kwargs):
            module = importlib.import_module("CTFd.plugins.photo_challenges.routes")
            func = getattr(module, func_name)
            return func(*args, **kwargs)
        return _view

    try:
        app.add_url_rule(
            "/api/v1/photo_challenges/upload",
            endpoint="photo_challenges.upload",
            view_func=_lazy_view("upload_photo_fallback"),
            methods=["POST"],
        )

        app.add_url_rule(
            "/api/v1/photo_challenges/status/<int:challenge_id>",
            endpoint="photo_challenges.status",
            view_func=_lazy_view("submission_status_fallback"),
            methods=["GET"],
        )

        try:
            rules = [r.rule for r in app.url_map.iter_rules() if 'photo_challenges' in r.endpoint or 'photo_challenges' in r.rule]
            app.logger.info(f"photo_challenges: fallback rules added, matching rules: {rules}")
        except Exception:
            app.logger.info("photo_challenges: fallback rules added (unable to enumerate url_map)")
    except Exception:
        app.logger.exception("photo_challenges: failed to add fallback url rules")

    # Register an admin page and add it to the Admin Plugins menu so
    # administrators can review/approve/reject submissions from the UI.
    try:
        from .routes import admin_page
        from CTFd.plugins import register_admin_plugin_menu_bar

        # Expose the admin landing page at `/admin/photo_evidence`.
        app.add_url_rule(
            "/admin/photo_evidence",
            endpoint="photo_challenges.admin",
            view_func=admin_page,
            methods=["GET"],
        )

        # Add the menu entry under the admin Plugins dropdown. Use a
        # relative route (no leading slash) so templates build the final
        # /admin/... URL consistently.
        register_admin_plugin_menu_bar("Photo Submissions", "photo_evidence")
        app.logger.info("photo_challenges: registered admin menu link target 'photo_evidence'")

        # Emit diagnostic info about matching URL rules so we can confirm
        # registration on startup.
        try:
            rules = [r.rule for r in app.url_map.iter_rules() if 'photo_challenges' in r.endpoint or r.rule.endswith('/admin/photo_evidence') or r.rule.endswith('/admin/photo_evidence/')]
            app.logger.info(f"photo_challenges: url_map rules matching expected admin route: {rules}")
        except Exception:
            app.logger.exception("photo_challenges: failed to enumerate url_map after admin registration")
    except Exception:
        app.logger.exception("photo_challenges: failed to register admin admin menu link")