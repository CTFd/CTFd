import datetime
import threading

from flask import Blueprint, render_template, request, abort
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_user_page_menu_bar, register_admin_plugin_menu_bar
from CTFd.cache import cache

from .utils import database
from .utils import config
from .utils import bloods


def load(app):
  app.db.create_all()

  # on startup, init config and perform initial sync
  with app.app_context():
    config.init()

    try:
      bloods.sync()
      print("[bloods plugin] initial sync completed successfully on startup!")
    except Exception as e:
      print(f"[bloods plugin] initial sync (during startup) error: {e}")

  # bloods blueprint
  bloods_bp = Blueprint("bloods", __name__, template_folder="templates")

  @bloods_bp.route("/admin/bloods", methods=["GET", "POST"])
  @admins_only
  def bloods_admin_dashboard():
    if request.method == "POST":
      action = request.form.get("action")
      
      # reset config
      if action == "reset":
        # reset the config
        config.reset()
        
        # perform sync
        bloods.sync()
        
        return render_template(
          "admin_bloods.html",
          success=True,
          message="config has been reset to default",
          no_bloods=int(config.get_no_bloods() or 3),
          config_key_no_bloods=config.key_no_bloods,
          config_key_blood_val=config.key_blood_val,
          config_get_blood_val=config.get_blood_val,
          config_key_blood_title=config.key_blood_title,
          config_get_blood_title=config.get_blood_title,
          config_key_blood_icon=config.key_blood_icon,
          config_get_blood_icon=config.get_blood_icon,
          config_key_filter_mode=config.key_filter_mode,
          config_get_filter_mode=config.get_filter_mode,
          config_key_filter_list=config.key_filter_list,
          config_get_filter_list=config.get_filter_list
        )
        
      # save config
      elif action == "save":
        # update the config
        config.set(request.form)

        # perform sync
        bloods.sync()
        
        return render_template(
          "admin_bloods.html",
          success=True,
          message="config has been updated",
          no_bloods=int(config.get_no_bloods() or 3),
          config_key_no_bloods=config.key_no_bloods,
          config_key_blood_val=config.key_blood_val,
          config_get_blood_val=config.get_blood_val,
          config_key_blood_title=config.key_blood_title,
          config_get_blood_title=config.get_blood_title,
          config_key_blood_icon=config.key_blood_icon,
          config_get_blood_icon=config.get_blood_icon,
          config_key_filter_mode=config.key_filter_mode,
          config_get_filter_mode=config.get_filter_mode,
          config_key_filter_list=config.key_filter_list,
          config_get_filter_list=config.get_filter_list
        )
      
      # invalid action
      else:
        return abort(400)

    elif request.method == "GET":
      return render_template(
        "admin_bloods.html",
        no_bloods=int(config.get_no_bloods() or 3),
        config_key_no_bloods=config.key_no_bloods,
        config_key_blood_val=config.key_blood_val,
        config_get_blood_val=config.get_blood_val,
        config_key_blood_title=config.key_blood_title,
        config_get_blood_title=config.get_blood_title,
        config_key_blood_icon=config.key_blood_icon,
        config_get_blood_icon=config.get_blood_icon,
        config_key_filter_mode=config.key_filter_mode,
        config_get_filter_mode=config.get_filter_mode,
        config_key_filter_list=config.key_filter_list,
        config_get_filter_list=config.get_filter_list
      )
      
    else:
      return abort(400)

  @bloods_bp.route("/bloods", methods=["GET"])
  def bloods_page():
    if request.method == "GET":
      bloods = []

      results = database.get_all()
      for row in results:
        bloods.append({
          "challenge_name": row.challenge_name,
          "challenge_id": row.challenge_id,
          "user_name": row.user_name,
          "user_id": row.user_id,
          "team_name": row.team_name if row.team_name else "None",
          "team_id": row.team_id,
          "date": row.date,
          "position": row.position,
        })
      
      bloods.sort(
        key=lambda x: x["date"] if x["date"] else datetime.datetime.min,
        reverse=True,
      )
      
      return render_template("bloods.html", bloods=bloods)
    
    else:
      return abort(400)
    
  app.register_blueprint(bloods_bp)

  # register the admin dashboard in the admin menu bar
  register_admin_plugin_menu_bar("bloods", "/admin/bloods")

  # register the page in the user menu bar
  register_user_page_menu_bar("Bloods", "/bloods")

  # perform sync on every action that could have caused a relevant change
  @app.after_request
  def trigger_sync(response):
    if request.method in ["POST", "PATCH", "DELETE"]:
      # check if the requested path matches any endpoint that requires a sync
      path = request.path
      endpoints = [
        "/api/v1/challenges",
        "/api/v1/users", 
        "/api/v1/teams",
        "/api/v1/solves",
        "/api/v1/submissions"
      ]
      
      if not any(path.startswith(ep) for ep in endpoints):
        return response
      
      # check debounce
      if cache.get("bloods_sync_lock"):
        return response
    
      # set debounce
      cache.set("bloods_sync_lock", True, timeout=5)
      
      # run the sync in a background thread so it doesn't block the request
      app_ctx = app.app_context()
      def run_sync_thread(ctx):
        with ctx:
          try:
            bloods.sync()
          except Exception as e:
            print(f"[bloods plugin] sync error: {e}")
            cache.delete("bloods_sync_lock") # it can be helpful to release the debounce, as the sync didn't complete successfully
      
      threading.Thread(target=run_sync_thread, args=(app_ctx,)).start()

      return response
    
    else:
      return response
  
