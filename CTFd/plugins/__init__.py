from CTFd.models import db, WrongKeys, Pages, Config, Tracking, Teams, Containers, ip2long, long2ip
from flask import current_app as app, g, request, redirect, url_for, session, render_template, abort
import os
import importlib
import glob


def init_plugins(app):
    modules = glob.glob(os.path.dirname(__file__) + "/*")
    for module in modules:
        if os.path.isdir(module):
            module = '.' + os.path.basename(module)
            module = importlib.import_module(module, package='CTFd.plugins')
            module.load(app)
            print " * Loaded module,", module