from tests.helpers import create_ctfd, destroy_ctfd, setup_ctfd


def test_plugin_load():
    """Test that external plugins are correctly loaded"""
    app = create_ctfd(setup=False, enable_plugins=True)
    assert app.plugin_2_loaded


def test_plugin_dependency():
    """Test that plugin dependency works"""
    app = create_ctfd(setup=False, enable_plugins=True)
    assert app.plugin_1_loaded
