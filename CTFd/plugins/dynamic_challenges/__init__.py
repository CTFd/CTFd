from __future__ import division  # Use floating point for math calculations

import math

from flask import Blueprint

from CTFd.models import Challenges, Solves, db
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.migrations import upgrade
from CTFd.utils.modes import get_model


class DynamicChallenge(Challenges):
    __mapper_args__ = {"polymorphic_identity": "dynamic"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )
    initial = db.Column(db.Integer, default=0)
    minimum = db.Column(db.Integer, default=0)
    decay = db.Column(db.Integer, default=0)

    def __init__(self, *args, **kwargs):
        super(DynamicChallenge, self).__init__(**kwargs)
        self.value = kwargs["initial"]


class DynamicValueChallenge(BaseChallenge):
    id = "dynamic"  # Unique identifier used to register challenges
    name = "dynamic"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/dynamic_challenges/assets/create.html",
        "update": "/plugins/dynamic_challenges/assets/update.html",
        "view": "/plugins/dynamic_challenges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/dynamic_challenges/assets/create.js",
        "update": "/plugins/dynamic_challenges/assets/update.js",
        "view": "/plugins/dynamic_challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/dynamic_challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "dynamic_challenges",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = DynamicChallenge

    @classmethod
    def calculate_value(cls, challenge):
        Model = get_model()

        solve_count = (
            Solves.query.join(Model, Solves.account_id == Model.id)
            .filter(
                Solves.challenge_id == challenge.id,
                Model.hidden == False,
                Model.banned == False,
            )
            .count()
        )

        # If the solve count is 0 we shouldn't manipulate the solve count to
        # let the math update back to normal
        if solve_count != 0:
            # We subtract -1 to allow the first solver to get max point value
            solve_count -= 1

        # Handle situations where admins have entered a 0 decay
        # This is invalid as it can cause a division by zero
        if challenge.decay == 0:
            challenge.decay = 1

        # It is important that this calculation takes into account floats.
        # Hence this file uses from __future__ import division
        value = (
            ((challenge.minimum - challenge.initial) / (challenge.decay ** 2))
            * (solve_count ** 2)
        ) + challenge.initial

        value = math.ceil(value)

        if value < challenge.minimum:
            value = challenge.minimum

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
        challenge = DynamicChallenge.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "initial": challenge.initial,
            "decay": challenge.decay,
            "minimum": challenge.minimum,
            "description": challenge.description,
            "connection_info": challenge.connection_info,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
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
                value = float(value)
            setattr(challenge, attr, value)

        return DynamicValueChallenge.calculate_value(challenge)

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

        DynamicValueChallenge.calculate_value(challenge)


def load(app):
    upgrade(plugin_name="dynamic_challenges")
    CHALLENGE_CLASSES["dynamic"] = DynamicValueChallenge
    register_plugin_assets_directory(
        app, base_path="/plugins/dynamic_challenges/assets/"
    )
