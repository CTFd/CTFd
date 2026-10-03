"""
Atea admin styling

Adds the Atea look to the Admin Panel while the "atea" theme is selected.
The styles themselves live in the atea theme (assets/scss/admin.scss).
Selecting any other theme leaves the Admin Panel untouched.
"""

from flask import Response, redirect

from CTFd.constants.assets import Assets
from CTFd.plugins import register_admin_plugin_stylesheet
from CTFd.utils.config import ctf_theme

ATEA_THEME = "atea"
STYLESHEET_ROUTE = "/plugins/atea_admin/admin.css"


def load(app):
    @app.route(STYLESHEET_ROUTE)
    def atea_admin_stylesheet():
        if ctf_theme() != ATEA_THEME:
            return Response("", mimetype="text/css")
        return redirect(Assets.file("assets/scss/admin.scss", theme=ATEA_THEME))

    register_admin_plugin_stylesheet(STYLESHEET_ROUTE)
