import threading

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, abort
from CTFd.models import Challenges, Solves
from CTFd.utils import get_config
from CTFd.utils.user import get_current_user, get_current_team, authed, is_admin
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.plugins import register_admin_plugin_menu_bar, register_user_page_menu_bar
from CTFd.cache import cache

from .utils import writeups as wwriteups
from .utils import disabled_chals


# helper function
def has_solved_challenge(chal_id):
  mode = get_config("user_mode")
  if mode == "teams":
    team = get_current_team()
    if not team: return False
    
    return (
      Solves.query.filter_by(team_id=team.id, challenge_id=chal_id).first()
      is not None
    )
  
  else:
    user = get_current_user()
    if not user: return False
    
    return (
      Solves.query.filter_by(user_id=user.id, challenge_id=chal_id).first()
      is not None
    )

def load(app):
  app.db.create_all()

  # on startup, perform initial sync
  with app.app_context():
    try:
      wwriteups.sync()
      print("[bloodwriteupss plugin] initial sync completed successfully on startup!")
    except Exception as e:
      print(f"[writeups plugin] initial sync (during startup) error: {e}")

  # writeups blueprint
  writeups_bp = Blueprint("writeups", __name__, template_folder="templates")

  @writeups_bp.route("/api/v1/writeups/<int:chal_id>", methods=["GET"])
  def writeups_get_api(chal_id):
    # not authed
    if not authed():
      return jsonify({"success": False, "error": "Not authenticated"}), 403

    # check if challenge is disabled
    if not disabled_chals.get_chal_status(chal_id):
      return (
        jsonify(
          {"success": False, "error": "Writeups disabled for this challenge."}
        ),
        403,
      )

    # has no solution for the challenge and is not an admin
    if not (has_solved_challenge(chal_id) or is_admin()):
      return jsonify({"success": False, "error": "Solve required."}), 403

    # prepare writeups data
    writeups_data = [
      {
        "user_id": s.user_id,
        "user_name": s.user.name,
        "code": s.code,
        "submitted_at": s.submitted_at.strftime("%Y-%m-%d %H:%M"),
      }
      for s in wwriteups.get_all_for_chal(chal_id)
    ]
    
    return jsonify({"success": True, "current_user_id": get_current_user().id, "solutions": writeups_data})

  @writeups_bp.route("/api/v1/writeups/<int:chal_id>", methods=["POST"])
  def writeups_modify_api(chal_id):
    data = request.get_json()
    if not data: return jsonify({"success": False, "error": "no request data"}), 400
    
    # not authed
    if not authed():
      return jsonify({"success": False, "error": "Not authenticated"}), 403

    # check if challenge is disabled
    if not disabled_chals.get_chal_status(chal_id):
      return (jsonify({"success": False, "error": "Writeups disabled for this challenge."}), 403,)
    
    # has no solution for the challenge and is not an admin
    if not (has_solved_challenge(chal_id) or is_admin()):
      return jsonify({"success": False, "error": "Solve required."}), 403

    action = data.get("action")

    # delete existing writeup
    if action == "delete":
      if wwriteups.delete_writeup_for_user_and_chal(chal_id, get_current_user().id):
        return jsonify({"success": True})
      
      else:
        return jsonify({"success": False, "error": "can't delete writeup"}), 400

    # submit writeup
    elif action == "submit":
      content = data.get("code", "").strip()
      if wwriteups.submit(content, chal_id, get_current_user().id):
        return jsonify({"success": True})
      
      else:
        return jsonify({"success": False, "error": "can't submit writeup"}), 400

    # invalid action
    else:
      return jsonify({"success": False, "error": "Invalid action."}), 400

  @writeups_bp.route("/admin/writeups", methods=["GET", "POST"])
  @admins_only
  def writeups_admin_dashboard():
    def render_admin_dashboard():
      writeups = wwriteups.get_all()
      all_challenges = Challenges.query.all()
      disabled_chal_ids = [d.challenge_id for d in disabled_chals.get_all()]

      return render_template(
        "admin_writeups.html",
        writeups=writeups,
        all_challenges=all_challenges,
        disabled_chal_ids=disabled_chal_ids,
      )
    
    if request.method == "POST":
      action = request.form.get("action")

      # delete all writeups
      if action == "delete_all":
        wwriteups.delete_all()
        
      # delete all user's writeups
      elif action == "delete_user":
        target_user = request.form.get("target_user_id")
        wwriteups.delete_all_for_user(target_user)
        
      # delete all challenge's writeups
      elif action == "delete_challenge":
        target_chal = request.form.get("target_challenge_id")
        wwriteups.delete_all_for_chal(target_chal)

      # delete a single writeup
      elif action == "delete_writeup":
        writeup_id = request.form.get("writeup_id")
        wwriteups.delete_writeup(writeup_id)
      
      # enable/disable writeups for challenge
      elif action == "set_chal_status":
        chal_id = request.form.get("challenge_id")
        status = request.form.get("status") == "enabled"
        disabled_chals.set_chal_status(chal_id, status)
      
      # invalid action
      else:
        return abort(400)
      
      return render_admin_dashboard()

    elif request.method == "GET":
      return render_admin_dashboard()
    
    else:
      return abort(400)

  @writeups_bp.route("/writeups", methods=["GET"])
  @authed_only
  def writeups_page():
    # get the user's/team's solves
    user_mode = get_config("user_mode")
    if user_mode == "teams":
      team = get_current_team()
      solves = Solves.query.filter_by(team_id=team.id).all() if team else []
    else:
      user = get_current_user()
      solves = Solves.query.filter_by(user_id=user.id).all()

    # get disabled chals
    disabled_chal_ids = [d.challenge_id for d in disabled_chals.get_all()]
    
    # find the relevant chals
    relevant_chal_ids = [
      s.challenge_id for s in solves if s.challenge_id not in disabled_chal_ids
    ]

    chals = (
      Challenges.query.filter(Challenges.id.in_(relevant_chal_ids)).all()
      if relevant_chal_ids
      else []
    )

    return render_template("writeups.html", challenges=chals)

  app.register_blueprint(writeups_bp)

  # register the admin dashboard in the admin menu bar
  register_admin_plugin_menu_bar("writeups", "/admin/writeups")
  
  # register the page in the user menu bar
  register_user_page_menu_bar("Writeups", "/writeups")

  # trigger cleanup when challenges, users, teams, or solutions are modified
  @app.after_request
  def trigger_writeups_cleanup(response):
    if request.method in ["POST", "PATCH", "DELETE"]:
      # check if the path matches any endpoint that requires a sync
      path = request.path
      endpoints = [
        "/api/v1/challenges",
        "/api/v1/users",
        "/api/v1/teams",
        "/api/v1/solves",
        "/api/v1/submissions"
      ]
      
      if not any(request.path.startswith(ep) for ep in endpoints):
        return response
      
      # check debounce
      if cache.get("writeups_sync_lock"):
        return response
    
      # set debounce
      cache.set("writeups_sync_lock", True, timeout=5)
      
      # run the sync in a background thread so it doesn't block the request
      app_ctx = app.app_context()
      def run_sync_thread(ctx):
        with ctx:
          try:
            wwriteups.sync()
          except Exception as e:
            print(f"[writeups plugin] sync error: {e}")
            cache.delete("writeups_sync_lock") # it can be helpful to release the debounce, as the sync didn't complete successfully
      
      threading.Thread(target=run_sync_thread, args=(app_ctx,)).start()

      return response
    
    else:
      return response