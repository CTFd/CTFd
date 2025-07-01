from CTFd.cache import cache
from CTFd.utils import _get_asset_json, get_asset_json, get_config, set_config
from CTFd.models import Configs, db
from CTFd.utils.helpers import markup
from flask import current_app,url_for
import os


def load(app):
    cache.delete_memoized(_get_asset_json, os.path.join(
            current_app.root_path, "plugins/emailnotifications/staticAssets/manifest.json"))
    return 

class _LuaAsset():
    def __init__(self,directory):
        self.directory = directory
    def manifest(self, _return_none_on_load_failure=False):
        file_path = os.path.join(
            current_app.root_path, "plugins",self.directory,"staticAssets","manifest.json"
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

    def js(self, asset_key, type="module", defer=False, extra=""):
        asset = self.manifest()[asset_key]
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
            i = self.manifest()[i]["file"]
            url = url_for(self.directory+".static", filename=i)
            html += f'<script {_attrs} src="{url}"></script>'
        url = url_for(self.directory+".static", filename=entry)
        html += f'<script {_attrs} src="{url}"></script>'
        return markup(html)

def toggle_config(key):
    db.session.commit()
    config = Configs.query.filter(Configs.key == key).first()
    if config:
        value = get_config(key)
        if value:
            set_config(key,'false')
            return False
        else:
            set_config(key,'true')
            return True
    else:
        conf = Configs(key=key,value="true")
        db.session.add(conf)
        db.session.commit()
        return True

class ConfigPanel():
    def __init__(self, name,desc,toggle,config):
        self.name = name
        self.desc = desc
        self.toggle = toggle
        self.config = config
