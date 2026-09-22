from flask import Blueprint, render_template, request, abort
from CTFd.utils.decorators import admins_only
from CTFd.plugins import register_admin_plugin_menu_bar

from .utils import config

def load(app):
  # google analytics integr blueprint
  google_analytics_integr_bp = Blueprint("google_analytics_integr", __name__, template_folder="templates")

  @google_analytics_integr_bp.route("/admin/google_analytics_integr", methods=["GET", "POST"])
  @admins_only
  def admin_google_analytics_integr_dashboard():
    if request.method == "POST":
      action = request.form.get("action")
      
      if action == "clear":
        config.set_script("")
        config.set_is_enabled(False)
        
        return render_template(
          "admin_google_analytics_integr.html", 
          script=config.get_script(),
          enabled=config.get_is_enabled(),
          success=True,
          msg="script cleared and disabled successfully"
        )
        
      elif action == "save":
        # update the script
        script = request.form.get("google_analytics_script")
        config.set_script(script)
        
        # update is_enabled
        is_enabled = request.form.get("google_analytics_enabled") == "on" 
        config.set_is_enabled(is_enabled)
        
        return render_template(
          "admin_google_analytics_integr.html", 
          script=config.get_script(),
          enabled=config.get_is_enabled(),
          success=True,
          msg="config updated successfully"
        )
      
      else:
        return abort(400)
    
    elif request.method == "GET":
      return render_template(
        "admin_google_analytics_integr.html", 
        script=config.get_script(),
        enabled=config.get_is_enabled()
      )
    
    else:
      return abort(400)

  app.register_blueprint(google_analytics_integr_bp)
  
  # register the admin dashboard in the admin menu bar
  register_admin_plugin_menu_bar("google analytics integr", "/admin/google_analytics_integr")

  # inject the script
  @app.after_request
  def inject_script(response):
    # check if enabled
    if not config.get_is_enabled():
      return response
      
    # ignore admin dashboards
    if request.path.startswith("/admin"):
      return response
      
    if response.mimetype == 'text/html' and not response.direct_passthrough:
      script = config.get_script()
      
      if script:
        data = response.get_data()
        
        # inject the script right before the closing </head> tag
        if b"</head>" in data:
          script_bytes = script.encode('utf-8')
          response.set_data(data.replace(b'</head>', script_bytes + b'\n</head>'))
    
    return response
