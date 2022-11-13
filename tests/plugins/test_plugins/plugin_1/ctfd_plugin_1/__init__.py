from CTFd.exceptions import PluginDependencyException


def test_load(app):
    if 'ctfd_plugin_2' not in app.plugins_loaded:
        raise PluginDependencyException(['ctfd_plugin_2'])
    app.plugin_1_loaded = True
