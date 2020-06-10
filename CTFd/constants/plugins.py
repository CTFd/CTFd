from flask import current_app

from CTFd.plugins import get_admin_plugin_menu_bar, get_user_page_menu_bar
from CTFd.utils.helpers import markup
from CTFd.utils.plugins import get_registered_scripts, get_registered_stylesheets


class _PluginWrapper:
    @property
    def scripts(self):
        application_root = current_app.config.get("APPLICATION_ROOT")
        subdir = application_root != "/"
        scripts = []
        for script in get_registered_scripts():
            if script.startswith("http"):
                scripts.append(f'<script defer src="{script}"></script>')
            elif subdir:
                scripts.append(
                    f'<script defer src="{application_root}/{script}"></script>'
                )
            else:
                scripts.append(f'<script defer src="{script}"></script>')
        return markup("\n".join(scripts))

    @property
    def styles(self):
        application_root = current_app.config.get("APPLICATION_ROOT")
        subdir = application_root != "/"
        _styles = []
        for stylesheet in get_registered_stylesheets():
            if stylesheet.startswith("http"):
                _styles.append(
                    f'<link rel="stylesheet" type="text/css" href="{stylesheet}">'
                )
            elif subdir:
                _styles.append(
                    f'<link rel="stylesheet" type="text/css" href="{application_root}/{stylesheet}">'
                )
            else:
                _styles.append(
                    f'<link rel="stylesheet" type="text/css" href="{stylesheet}">'
                )
        return markup("\n".join(_styles))

    @property
    def user_menu_pages(self):
        return get_user_page_menu_bar()

    @property
    def admin_menu_pages(self):
        return get_admin_plugin_menu_bar()


Plugins = _PluginWrapper()
