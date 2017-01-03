import glob
import importlib
import os


def init_plugins(app):
    modules = glob.glob(os.path.dirname(__file__) + "/*")
    for module in modules:
        if os.path.isdir(module):
            module = '.' + os.path.basename(module)
            module = importlib.import_module(module, package='CTFd.plugins')
            module.load(app)
            print(" * Loaded module, %s" % module)
