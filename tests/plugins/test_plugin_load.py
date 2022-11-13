from CTFd.exceptions import PluginDependencyException
from tests.helpers import create_ctfd


def test_plugin_load():
    """Test that external plugins are correctly loaded"""
    app = create_ctfd(setup=False, enable_plugins=True)
    assert app.plugin_2_loaded


def test_plugin_dependency():
    """Test that plugin dependency works"""
    app = create_ctfd(setup=False, enable_plugins=True)
    assert app.plugin_1_loaded


def test_plugin_bad_dependency():
    assert PluginDependencyException('bad').dependencies == []
