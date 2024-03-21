import os

from flask import current_app, url_for

from CTFd.utils import get_asset_json
from CTFd.utils.config import ctf_theme
from CTFd.utils.helpers import markup


class _AssetsWrapper:
    def manifest(self, theme=None):
        if theme is None:
            theme = ctf_theme()
        manifest = os.path.join(
            current_app.root_path, "themes", theme, "static", "manifest.json"
        )
        return get_asset_json(path=manifest)

    def js(self, asset_key, theme=None, defer=True):
        if theme is None:
            theme = ctf_theme()
        asset = self.manifest(theme=theme)[asset_key]
        entry = asset["file"]
        imports = asset.get("imports", [])
        extra_attr = "defer " if defer else ""
        html = ""
        for i in imports:
            # TODO: Needs a better recursive solution
            i = self.manifest(theme=theme)[i]["file"]
            url = url_for("views.themes_beta", theme=theme, path=i)
            html += f'<script {extra_attr}type="module" src="{url}"></script>'
        url = url_for("views.themes_beta", theme=theme, path=entry)
        html += f'<script {extra_attr}type="module" src="{url}"></script>'
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
