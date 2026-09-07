from flask import Blueprint, render_template, request, abort
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_user_page_menu_bar, register_admin_plugin_menu_bar

from .utils import database

def load(app):
  app.db.create_all()

  # credits blueprint
  credits_bp = Blueprint("credits", __name__, template_folder="templates")

  @credits_bp.route("/credits", methods=["GET"])
  def credits_page():
    if request.method == "GET":
      all_credits = database.Credits.query.all()
      return render_template("credits.html", credits=all_credits)
    
    else:
      return abort(400)

  @credits_bp.route("/admin/credits", methods=["GET", "POST"])
  @admins_only
  def admin_credits_dashboard():
    if request.method == "POST":
      action = request.form.get("action")
      
      if action == "add":
        content = request.form.get("content")
        if content:
          database.add(content)

      elif action == "delete":
        credit_id = request.form.get("credit_id")
        database.remove(credit_id)
      
      elif action == "delete_all":
        database.remove_all()
      
      all_credits = database.get_all()
      return render_template("admin_credits.html", credits=all_credits)
    
    elif request.method == "GET":
      all_credits = database.get_all()
      return render_template("admin_credits.html", credits=all_credits)
    
    else:
      return abort(400)

  app.register_blueprint(credits_bp)

  # register the admin dashboard in the admin menu bar
  register_admin_plugin_menu_bar("credits", "/admin/credits")
  
  # register the page in the user menu bar
  register_user_page_menu_bar("Credits", "/credits")
