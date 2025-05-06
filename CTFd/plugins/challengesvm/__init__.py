from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES
from CTFd.plugins.challenges import BaseChallenge
from flask import Blueprint
from CTFd.models import Challenges, db
from CTFd.exceptions.challenges import ChallengeCreateException

class VMChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "vm"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    vm_address = db.Column(db.String(256), nullable=True)  # Exemplo de campo para a VM
    credentials = db.Column(db.String(256), nullable=True)  # Exemplo de credenciais da VM

    def __init__(self, *args, **kwargs):
        super(VMChallenge, self).__init__(**kwargs)
        try:
            self.vm_address = kwargs["vm_address"]
            self.credentials = kwargs["credentials"]
        except KeyError:
            raise ChallengeCreateException("Missing VM details for challenge")



class VMChallengeType(BaseChallenge):
    id = "vm"  # Identificador único do tipo de desafio
    name = "Virtual Machine"  # Nome do tipo de desafio
    templates = {
        'create': '/plugins/challengesvm/assets/create.html',
        'update': '/plugins/challengesvm/assets/update.html',
        'view': '/plugins/challengesvm/assets/view.html',
    }
    scripts = {
        'create': '/plugins/challengesvm/assets/create.js',
        'update': '/plugins/challengesvm/assets/update.js',
        'view': '/plugins/challengesvm/assets/view.js',
    }
    route = "/plugins/challengesvm/assets/"
    blueprint = Blueprint(
        "challengesvm",
        __name__,
        template_folder="templates",
        static_folder="assets"
    )
    challenge_model = VMChallenge

def load(app):
    # Registra o tipo de desafio "vm" no CTFd
    CHALLENGE_CLASSES["vm"] = VMChallengeType
    # Registra os arquivos estáticos e templates do plugin
    register_plugin_assets_directory(app, base_path="/plugins/challengesvm/assets/")
