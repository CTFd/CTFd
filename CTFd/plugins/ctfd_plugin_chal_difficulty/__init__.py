import os
from flask import Blueprint, render_template, request, abort, jsonify
from CTFd.models import Challenges
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_admin_plugin_menu_bar, register_plugin_script

from .utils import database
from .utils import config
from .utils import chal_difficulties


def load(app):
  app.db.create_all()

  # on startup, init config config
  with app.app_context():
    config.init()
    chal_difficulties.sync()

  # chal difficulties blueprint
  chal_difficulties_bp = Blueprint(
    "chal_difficulty",
    __name__,
    template_folder="templates",
    static_folder="assets",
    static_url_path="/plugins/ctfd_plugin_chal_difficulties/assets",
  )

  @chal_difficulties_bp.route("/admin/chal_difficulties", methods=["GET", "POST"])
  @admins_only
  def admin_chal_difficulties_dashboard():
    def render_admin_dashboard(with_success: bool):
      chals = Challenges.query.order_by(Challenges.category, Challenges.id).all()
      diffs = {d.challenge_id: d.difficulty for d in database.get_all()}
      no_difficulties = int(config.get_no_difficulties() or 3)

      chal_data = []
      for c in chals:
        val = diffs.get(c.id, "0")
        chal_data.append(
          {
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "difficulty": val,
          }
        )

      return render_template(
        "admin_chal_difficulty.html",
        challenges=chal_data,
        no_difficulties=no_difficulties,
        success=with_success
      )
    
    if request.method == "POST":
      # set
      chal_difficulties.set(request.form)

      # sync
      chal_difficulties.sync()
      
      return render_admin_dashboard(True)
    
    elif request.method == "GET":
      return render_admin_dashboard(False)
    
    else:
      return abort(400)

  @chal_difficulties_bp.route("/api/v1/difficulties", methods=["GET"])
  def chal_difficulties_api():
    if request.method == "GET":
      no_difficulties = int(config.get_no_difficulties() or 3)
      entries = {d.challenge_id: d.difficulty for d in database.get_all()}
      return jsonify({"success": True, "no_difficulties": no_difficulties, "entries": entries})
    
    else:
      return abort(400)

  app.register_blueprint(chal_difficulties_bp)

  # register the admin dashboard in the admin menu bar
  register_admin_plugin_menu_bar("chal difficulties", "/admin/chal_difficulties")
  
  # inject the javascript file into the theme
  register_plugin_script("/plugins/ctfd_plugin_chal_difficulties/assets/difficulty.js")
