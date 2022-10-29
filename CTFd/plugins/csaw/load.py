# Plugin Entry Point
from CTFd.api import CTFd_API_v1
from flask import render_template
from CTFd.plugins.csaw.views import view_manage_regions, view_settings
from CTFd.plugins.csaw.api.namespace import csaw_namespace
from CTFd.utils.decorators import admins_only


def load(app):
    app.view_functions["views.settings"] = view_settings
    # app.route("/manage/regions", methods=["GET"])(view_manage_regions)
    # @app.route("/manage/regions", methods=["GET", "POST"])
    # @admins_only
    # def view_manage_regions():
    # return render_template("manage_regions.html")
    CTFd_API_v1.add_namespace(csaw_namespace, "/csaw")
