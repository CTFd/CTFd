import glob
import importlib
import os
from collections import namedtuple

from flask import current_app as app
from flask import send_file, send_from_directory, url_for

from CTFd.exceptions import PluginDependencyException
from CTFd.utils.config.pages import get_pages
from CTFd.utils.decorators import admins_only as admins_only_wrapper
from CTFd.utils.plugins import override_template as utils_override_template
from CTFd.utils.plugins import (
    register_admin_script as utils_register_admin_plugin_script,
)
from CTFd.utils.plugins import (
    register_admin_stylesheet as utils_register_admin_plugin_stylesheet,
)
from CTFd.utils.plugins import register_script as utils_register_plugin_script
from CTFd.utils.plugins import register_stylesheet as utils_register_plugin_stylesheet

Menu = namedtuple("Menu", ["title", "route"])


def register_plugin_assets_directory(app, base_path, admins_only=False, endpoint=None):
    """
    Registers a directory to serve assets

    :param app: A CTFd application
    :param string base_path: The path to the directory
    :param boolean admins_only: Whether or not the assets served out of the directory should be accessible to the public
    :return:
    """
    base_path = base_path.strip("/")
    if endpoint is None:
        endpoint = base_path.replace("/", ".")

    def assets_handler(path):
        return send_from_directory(base_path, path)

    rule = "/" + base_path + "/<path:path>"
    app.add_url_rule(rule=rule, endpoint=endpoint, view_func=assets_handler)


def register_plugin_asset(app, asset_path, admins_only=False, endpoint=None):
    """
    Registers an file path to be served by CTFd

    :param app: A CTFd application
    :param string asset_path: The path to the asset file
    :param boolean admins_only: Whether or not this file should be accessible to the public
    :return:
    """
    asset_path = asset_path.strip("/")
    if endpoint is None:
        endpoint = asset_path.replace("/", ".")

    def asset_handler():
        return send_file(asset_path)

    if admins_only:
        asset_handler = admins_only_wrapper(asset_handler)
    rule = "/" + asset_path
    app.add_url_rule(rule=rule, endpoint=endpoint, view_func=asset_handler)


def override_template(*args, **kwargs):
    """
    Overrides a template with the provided html content.

    e.g. override_template('scoreboard.html', '<h1>scores</h1>')
    """
    utils_override_template(*args, **kwargs)


def register_plugin_script(*args, **kwargs):
    """
    Adds a given script to the base.html template which all pages inherit from
    """
    utils_register_plugin_script(*args, **kwargs)


def register_plugin_stylesheet(*args, **kwargs):
    """
    Adds a given stylesheet to the base.html template which all pages inherit from.
    """
    utils_register_plugin_stylesheet(*args, **kwargs)


def register_admin_plugin_script(*args, **kwargs):
    """
    Adds a given script to the base.html of the admin theme which all admin pages inherit from
    :param args:
    :param kwargs:
    :return:
    """
    utils_register_admin_plugin_script(*args, **kwargs)


def register_admin_plugin_stylesheet(*args, **kwargs):
    """
    Adds a given stylesheet to the base.html of the admin theme which all admin pages inherit from
    :param args:
    :param kwargs:
    :return:
    """
    utils_register_admin_plugin_stylesheet(*args, **kwargs)


def register_admin_plugin_menu_bar(title, route):
    """
    Registers links on the Admin Panel menubar/navbar

    :param name: A string that is shown on the navbar HTML
    :param route: A string that is the href used by the link
    :return:
    """
    am = Menu(title=title, route=route)
    app.admin_plugin_menu_bar.append(am)


def get_admin_plugin_menu_bar():
    """
    Access the list used to store the plugin menu bar

    :return: Returns a list of Menu namedtuples. They have name, and route attributes.
    """
    return app.admin_plugin_menu_bar


def register_user_page_menu_bar(title, route):
    """
    Registers links on the User side menubar/navbar

    :param name: A string that is shown on the navbar HTML
    :param route: A string that is the href used by the link
    :return:
    """
    p = Menu(title=title, route=route)
    app.plugin_menu_bar.append(p)


def get_user_page_menu_bar():
    """
    Access the list used to store the user page menu bar

    :return: Returns a list of Menu namedtuples. They have name, and route attributes.
    """
    pages = []
    for p in get_pages() + app.plugin_menu_bar:
        if p.route.startswith("http"):
            route = p.route
        else:
            route = url_for("views.static_html", route=p.route)
        pages.append(Menu(title=p.title, route=route))
    return pages


def bypass_csrf_protection(f):
    """
    Decorator that allows a route to bypass the need for a CSRF nonce on POST requests.

    This should be considered beta and may change in future versions.

    :param f: A function that needs to bypass CSRF protection
    :return: Returns a function with the _bypass_csrf attribute set which tells CTFd to not require CSRF protection.
    """
    f._bypass_csrf = True
    return f


def get_plugin_names():
    modules = sorted(glob.glob(app.plugins_dir + "/*"))
    blacklist = {"__pycache__"}
    plugins = []
    for module in modules:
        module_name = os.path.basename(module)
        if os.path.isdir(module) and module_name not in blacklist:
            plugins.append(module_name)
    return plugins


def get_plugin_module(plugin_name):
    # intensionally raise KeyError if plugin is not loaded
    return app.plugin_module[plugin_name]


def _load_plugins(app):
    unmet_deps = {}
    attempt_reload = True
    while attempt_reload:
        attempt_reload = False
        for plugin in get_plugin_names():
            if plugin in app.plugin_module:
                continue
            module = "." + plugin
            module = importlib.import_module(module, package="CTFd.plugins")
            try:
                module.load(app)
                for p in unmet_deps.keys():
                    if plugin in unmet_deps[p]:
                        unmet_deps[p].remove(plugin)
                    if not unmet_deps[p]:
                        print(f" ! Dependency fulfilled for {p}")
                        attempt_reload = True
                if plugin in unmet_deps:
                    unmet_deps.pop(plugin)
                app.plugin_module[plugin] = module
                print(f" * Loaded module, {module}")
            except PluginDependencyException as e:
                unmet_deps[plugin] = set()
                for deps in e.dependencies:
                    if not get_plugin_module(deps):
                        unmet_deps[plugin].add(deps)
                        print(f" ! Module {module} requires module {deps} to be loaded")
                if not unmet_deps[plugin]:
                    print(f' ! Invalid dependencies for module {module}')


def init_plugins(app):
    """
    Searches for the load function in modules in the CTFd/plugins folder. This function is called with the current CTFd
    app as a parameter. This allows CTFd plugins to modify CTFd's behavior.

    :param app: A CTFd application
    :return:
    """
    app.admin_plugin_scripts = []
    app.admin_plugin_stylesheets = []
    app.plugin_scripts = []
    app.plugin_stylesheets = []

    app.admin_plugin_menu_bar = []
    app.plugin_menu_bar = []
    app.plugins_dir = os.path.dirname(__file__)
    app.plugin_module = {}

    if app.config.get("SAFE_MODE", False) is False:
        _load_plugins(app)
    else:
        print("SAFE_MODE is enabled. Skipping plugin loading.")

    app.jinja_env.globals.update(get_admin_plugin_menu_bar=get_admin_plugin_menu_bar)
    app.jinja_env.globals.update(get_user_page_menu_bar=get_user_page_menu_bar)
