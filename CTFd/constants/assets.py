import os

from flask import current_app, url_for

from CTFd.utils import get_asset_json
from CTFd.utils.config import ctf_theme
from CTFd.utils.helpers import markup


class _AssetsWrapper:
    def manifest(self, theme=None, _return_none_on_load_failure=False):
        if theme is None:
            theme = ctf_theme()
        file_path = os.path.join(
            current_app.root_path, "themes", theme, "static", "manifest.json"
        )

        try:
            manifest = get_asset_json(path=file_path)
        except FileNotFoundError as e:
            # This check allows us to determine if we are on a legacy theme and fallback if necessary
            if _return_none_on_load_failure:
                manifest = None
            else:
                raise e
        return manifest

    def js(self, asset_key, theme=None, type="module", defer=False, extra=""):
        if theme is None:
            theme = ctf_theme()
        asset = self.manifest(theme=theme)[asset_key]
        entry = asset["file"]
        imports = asset.get("imports", [])

        # Add in extra attributes. Note that type="module" imples defer
        _attrs = ""
        if type:
            _attrs = f'type="{type}" '
        if defer:
            _attrs += "defer "
        if extra:
            _attrs += extra

        html = ""
        for i in imports:
            # TODO: Needs a better recursive solution
            i = self.manifest(theme=theme)[i]["file"]
            url = url_for("views.themes_beta", theme=theme, path=i)
            html += f'<script {_attrs} src="{url}"></script>'
        url = url_for("views.themes_beta", theme=theme, path=entry)
        html += f'<script {_attrs} src="{url}"></script>'
        return markup(html)

    def css(self, asset_key, theme=None):
        if theme is None:
            theme = ctf_theme()
        asset = self.manifest(theme=theme)[asset_key]
        entry = asset["file"]
        url = url_for("views.themes_beta", theme=theme, path=entry)
        return markup(f'<link rel="stylesheet" href="{url}">')

    def file(self, asset_key, theme=None):
        if theme is None:
            theme = ctf_theme()
        asset = self.manifest(theme=theme)[asset_key]
        entry = asset["file"]
        return url_for("views.themes_beta", theme=theme, path=entry)


Assets = _AssetsWrapper()
