from flask import Blueprint, render_template, request, redirect, url_for, abort
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_user_page_menu_bar, register_admin_plugin_menu_bar

from .utils import database

def load(app):
  app.db.create_all()

  # disclaimers blueprint
  disclaimers_bp = Blueprint("disclaimers", __name__, template_folder="templates")

  @disclaimers_bp.route("/disclaimers", methods=["GET"])
  def disclaimers_page():
    if request.method == "GET":
      all_disclaimers = database.Disclaimers.query.all()
      return render_template("disclaimers.html", disclaimers=all_disclaimers)
    
    else:
      return abort(400)

  @disclaimers_bp.route("/admin/disclaimers", methods=["GET", "POST"])
  @admins_only
  def admin_disclaimers_dashboard():
    if request.method == "POST":
      action = request.form.get("action")
      
      if action == "add":
        content = request.form.get("content")
        if content:
          database.add(content)

      elif action == "delete":
        disclaimer_id = request.form.get("disclaimer_id")
        database.remove(disclaimer_id)
      
      elif action == "delete_all":
        database.remove_all()
      
      all_disclaimers = database.get_all()
      return render_template("admin_disclaimers.html", disclaimers=all_disclaimers)
    
    elif request.method == "GET":
      all_disclaimers = database.get_all()
      return render_template("admin_disclaimers.html", disclaimers=all_disclaimers)
    
    else:
      return abort(400)

  app.register_blueprint(disclaimers_bp)

  # register the admin dashboard in the admin menu bar
  register_admin_plugin_menu_bar("disclaimers", "/admin/disclaimers")
  
  # register the page in the user menu bar
  register_user_page_menu_bar("Disclaimers", "/disclaimers")
