import os
from flask import Blueprint, jsonify
from CTFd.models import Flags, Solves
from CTFd.utils.user import get_current_user, get_current_team, authed
from CTFd.utils import get_config
from CTFd.plugins import register_plugin_assets_directory, register_plugin_script
from CTFd.utils.decorators import authed_only


def load(app):
  reveal_bp = Blueprint("reveal_flag", __name__)

  # reveal flag blueprint
  @reveal_bp.route("/api/v1/reveal_flag/<int:chal_id>", methods=["GET"])
  @authed_only
  def reveal_flag_api(chal_id):
    # check if the challenge is solved
    mode = get_config("user_mode")
    if mode == "teams":
      # teams mode
      team = get_current_team()
      if not team:
        return jsonify({"success": False, "error": "No team found"}), 200
      
      solve = Solves.query.filter_by(
        team_id=team.id, challenge_id=chal_id
      ).first()
      
    else:
      # users mode
      user = get_current_user()
      solve = Solves.query.filter_by(
        user_id=user.id, challenge_id=chal_id
      ).first()

    if not solve:
      # challenge is not solved
      return jsonify({"success": False, "error": "Challenge not solved"}), 403
    
    else:
      # challenge is solved
      flag_list = [f.content for f in Flags.query.filter_by(challenge_id=chal_id).all()]

      return jsonify({"success": True, "flags": flag_list})

  app.register_blueprint(reveal_bp)

  # register assets
  register_plugin_assets_directory(
      app, base_path="/plugins/ctfd_plugin_reveal_flag/assets/"
  )

  # register injected script
  register_plugin_script("/plugins/ctfd_plugin_reveal_flag/assets/reveal_flag.js")
