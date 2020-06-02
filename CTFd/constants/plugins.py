from flask import current_app
from dataclasses import dataclass
from CTFd.utils import get_config
from markupsafe import Markup
from CTFd.utils.plugins import get_registered_scripts, get_registered_stylesheets


class _PluginWrapper:
    @property
    def scripts(self):
        application_root = current_app.config.get("APPLICATION_ROOT")
        subdir = application_root != "/"
        scripts = []
        for script in get_registered_scripts():
            if script.startswith('http'):
                scripts.append(f'<script defer src="{script}"></script>')
            elif subdir:
                scripts.append(f'<script defer src="{application_root}/{script}"></script>')
            else:
                scripts.append(f'<script defer src="{script}"></script>')
        return Markup("\n".join(scripts))

    @property
    def styles(self):
        application_root = current_app.config.get("APPLICATION_ROOT")
        subdir = application_root != "/"
        _styles = []
        for stylesheet in get_registered_stylesheets():
            if stylesheet.startswith('http'):
                _styles.append(f'<link rel="stylesheet" type="text/css" href="{stylesheet}">')
            elif subdir:
                _styles.append(f'<link rel="stylesheet" type="text/css" href="{application_root}/{script}">')
            else:
                _styles.append(f'<link rel="stylesheet" type="text/css" href="{stylesheet}">')
        return Markup("\n".join(_styles))


Plugins = _PluginWrapper()
