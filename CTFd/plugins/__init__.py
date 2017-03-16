import glob
import importlib
import os


def init_plugins(app):
    modules = glob.glob(os.path.dirname(__file__) + "/*")
    blacklist = {'keys', 'challenges', '__pycache__'}
    for module in modules:
        module_name = os.path.basename(module)
        if os.path.isdir(module) and module_name not in blacklist:
            module = '.' + module_name
            module = importlib.import_module(module, package='CTFd.plugins')
            module.load(app)
            print(" * Loaded module, %s" % module)
