import os
from flask import Blueprint, render_template, request, abort
from CTFd.models import db
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_admin_plugin_menu_bar, register_user_page_menu_bar

from .utils import database


def load(app):
  app.db.create_all()

  # faqs blueprint
  faqs_bp = Blueprint("faqs", __name__, template_folder="templates")

  @faqs_bp.route("/faqs", methods=["GET"])
  def faqs_page():
    if request.method == "GET":
      faqs = database.get_all()
      return render_template("faqs.html", faqs=faqs)
    
    else:
      return abort(400)
    
  @faqs_bp.route("/admin/faqs", methods=["GET", "POST"])
  @admins_only
  def admin_faqs_dashboard():
    if request.method == "POST":
      action = request.form.get("action")
      
      # add faq
      if action == "add":
        question = request.form.get("question")
        answer = request.form.get("answer")
        if question and answer:
          database.add(question=question.strip(), answer=answer.strip())
      
      # delete faq
      elif action == "delete":
        faq_id = request.form.get("faq_id")
        if faq_id:
          database.remove(faq_id)
      
      # delete all faqs
      elif action == "delete_all":
        database.remove_all()
      
      faqs = database.get_all()
      return render_template("admin_faqs.html", faqs=faqs)
    
    elif request.method == "GET":
      faqs = database.get_all()
      return render_template("admin_faqs.html", faqs=faqs)
    
    else:
      return abort(400)

  app.register_blueprint(faqs_bp)
  
  # register the admin dashboard in the admin menu bar
  register_admin_plugin_menu_bar("faqs", "/admin/faqs")
  
  # register the page in the user menu bar
  register_user_page_menu_bar("FAQs", "/faqs")
