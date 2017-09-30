import glob
import importlib
import os

from flask.helpers import safe_join
from flask import send_file, send_from_directory, abort
from CTFd.utils import admins_only as admins_only_wrapper


def register_plugin_assets_directory(app, base_path, admins_only=False):
    """
    Registers a directory to serve assets

    :param app: A CTFd application
    :param string base_path: The path to the directory
    :param boolean admins_only: Whether or not the assets served out of the directory should be accessible to the public
    :return:
    """
    base_path = base_path.strip('/')

    def assets_handler(path):
        return send_from_directory(base_path, path)

    if admins_only:
        asset_handler = admins_only_wrapper(assets_handler)

    rule = '/' + base_path + '/<path:path>'
    app.add_url_rule(rule=rule, endpoint=base_path, view_func=assets_handler)


def register_plugin_asset(app, asset_path, admins_only=False):
    """
    Registers an file path to be served by CTFd

    :param app: A CTFd application
    :param string asset_path: The path to the asset file
    :param boolean admins_only: Whether or not this file should be accessible to the public
    :return:
    """
    asset_path = asset_path.strip('/')

    def asset_handler():
        return send_file(asset_path)

    if admins_only:
        asset_handler = admins_only_wrapper(asset_handler)
    rule = '/' + asset_path
    app.add_url_rule(rule=rule, endpoint=asset_path, view_func=asset_handler)


def init_plugins(app):
    """
    Searches for the load function in modules in the CTFd/plugins folder. This function is called with the current CTFd
    app as a parameter. This allows CTFd plugins to modify CTFd's behavior.

    :param app: A CTFd application
    :return:
    """
    modules = glob.glob(os.path.dirname(__file__) + "/*")
    blacklist = {'keys', 'challenges', '__pycache__'}
    for module in modules:
        module_name = os.path.basename(module)
        if os.path.isdir(module) and module_name not in blacklist:
            module = '.' + module_name
            module = importlib.import_module(module, package='CTFd.plugins')
            module.load(app)
            print(" * Loaded module, %s" % module)
