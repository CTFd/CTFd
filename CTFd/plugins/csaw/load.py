# Plugin Entry Point
from CTFd.api import CTFd_API_v1
from CTFd.plugins.csaw.views import view_settings
from CTFd.plugins.csaw.api.namespace import csaw_namespace


def load(app):
    app.view_functions["views.settings"] = view_settings
    CTFd_API_v1.add_namespace(csaw_namespace, "/csaw")
