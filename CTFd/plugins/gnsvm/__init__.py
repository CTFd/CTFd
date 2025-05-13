# plugins/gnsvm/__init__.py
from flask import Blueprint

from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import BaseChallenge, CHALLENGE_CLASSES
from CTFd.models import db, Challenges
from CTFd.plugins.migrations import upgrade

class GNSChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "gns"}
#    id = db.Column(
#        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
#    )
    def __init__(self, *args, **kwargs):
        super(GNSChallenge, self).__init__(**kwargs)

class CTFdGnsvmChallenge(BaseChallenge):
    # Unique identifier and name for this challenge type
    id = "gns"
    name = "gns"
    # Templates and scripts for create/update/view (namespaced under /plugins/gnsvm/assets/)
    templates = {
        'create': '/plugins/gnsvm/assets/create.html',
        'update': '/plugins/gnsvm/assets/update.html',
        'view':   '/plugins/gnsvm/assets/view.html',
    }
    scripts = {
        'create': '/plugins/gnsvm/assets/create.js',
        'update': '/plugins/gnsvm/assets/update.js',
        'view':   '/plugins/gnsvm/assets/view.js',
    }
    # Inherit all behavior (create/update/attempt/solve/fail) from BaseChallenge
    # (BaseChallenge provides default implementations for a standard challenge.)
    route = "/plugins/gnsvm/assets/"
    blueprint = Blueprint(
        "gns_challenge", __name__, template_folder="templates", static_folder="assets")
    challenge_model = GNSChallenge

def load(app):
    upgrade(plugin_name="gns_challenge")
    # Register the new challenge class under the 'gnsvm' ID
    CHALLENGE_CLASSES['gns'] = CTFdGnsvmChallenge
    # Serve plugin assets at /plugins/gnsvm/assets/
    register_plugin_assets_directory(app, base_path='/plugins/gnsvm/assets/')
