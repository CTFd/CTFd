from flask import Blueprint

from CTFd.exceptions.challenges import (
    ChallengeCreateException,
    ChallengeUpdateException,
)
from CTFd.models import Challenges, db
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.VM_challenges.decay import DECAY_FUNCTIONS, logarithmic
from CTFd.plugins.migrations import upgrade


class VMChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "vm"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)
    function = db.Column(db.String(32), default="logarithmic")

    def __init__(self, *args, **kwargs):
        super(VMChallenge, self).__init__(**kwargs)
        try:
            self.value = kwargs["initial"]
        except KeyError:
            raise ChallengeCreateException("Missing initial value for challenge")


class VMValueChallenge(BaseChallenge):
    id = "vm"  # Unique identifier used to register challenges
    name = "vm"  # Name of a challenge type
    templates = (
        {  # Handlebars templates used for each aspect of challenge editing & viewing
            "create": "/plugins/VM_challenges/assets/create.html",
            "update": "/plugins/VM_challenges/assets/update.html",
            "view": "/plugins/VM_challenges/assets/view.html",
        }
    )
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/VM_challenges/assets/create.js",
        "update": "/plugins/VM_challenges/assets/update.js",
        "view": "/plugins/VM_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/VM_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "VM_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = VMChallenge

    @classmethod
    def calculate_value(cls, challenge):
        f = DECAY_FUNCTIONS.get(challenge.function, logarithmic)
        value = f(challenge)

        challenge.value = value
        db.session.commit()
        return challenge

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = VMChallenge.query.filter_by(id=challenge.id).first()
        data = super().read(challenge)
        data.update(
            {
                "initial": challenge.initial,
                "decay": challenge.decay,
                "minimum": challenge.minimum,
                "function": challenge.function,
            }
        )
        return data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "decay"):
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    raise ChallengeUpdateException(f"Invalid input for '{attr}'")
            setattr(challenge, attr, value)

        return VMValueChallenge.calculate_value(challenge)

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

        VMValueChallenge.calculate_value(challenge)


def load(app):
    upgrade(plugin_name="VM_challenges")
    CHALLENGE_CLASSES["VM"] = VMValueChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/VM_challenges/assets/"
    )
