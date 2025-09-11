from dataclasses import dataclass

from flask import Blueprint

from CTFd.exceptions.challenges import (
    ChallengeCreateException,
    ChallengeUpdateException,
)
from CTFd.models import (
    ChallengeFiles,
    Challenges,
    Fails,
    Flags,
    Hints,
    Partials,
    Solves,
    Tags,
    db,
)
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges.decay import DECAY_FUNCTIONS, logarithmic
from CTFd.plugins.challenges.logic import (
    challenge_attempt_all,
    challenge_attempt_any,
    challenge_attempt_team,
)
from CTFd.utils.uploads import delete_file
from CTFd.utils.user import get_ip


@dataclass
class ChallengeResponse:
    status: str
    message: str

    def __iter__(self):
        """Allow tuple-like unpacking for backwards compatibility."""
        # TODO: CTFd 4.0 remove this behavior as we should move away from the tuple strategy
        yield (True if self.status == "correct" else False)
        yield self.message


def calculate_value(challenge):
    f = DECAY_FUNCTIONS.get(challenge.function, logarithmic)
    value = f(challenge)

    challenge.value = value
    db.session.commit()
    return challenge


class BaseChallenge(object):
    id = None
    name = None
    templates = {}
    scripts = {}
    challenge_model = Challenges

    @classmethod
    def create(cls, request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        data = request.form or request.get_json()

        challenge = cls.challenge_model(**data)

        if challenge.function in DECAY_FUNCTIONS:
            if data.get("value") and not data.get("initial"):
                challenge.initial = data["value"]

            for attr in ("initial", "minimum", "decay"):
                db.session.rollback()
                if getattr(challenge, attr) is None:
                    raise ChallengeCreateException(
                        f"Missing '{attr}' but function is {challenge.function}"
                    )

        db.session.add(challenge)
        db.session.commit()

        # If the challenge is dynamic we should calculate a new value
        if challenge.function in DECAY_FUNCTIONS:
            return calculate_value(challenge)

        return challenge

    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "description": challenge.description,
            "attribution": challenge.attribution,
            "connection_info": challenge.connection_info,
            "next_id": challenge.next_id,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "logic": challenge.logic,
            "initial": challenge.initial if challenge.function != "static" else None,
            "decay": challenge.decay if challenge.function != "static" else None,
            "minimum": challenge.minimum if challenge.function != "static" else None,
            "function": challenge.function,
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
                try:
                    value = float(value)
                except (ValueError, TypeError):
                    db.session.rollback()
                    raise ChallengeUpdateException(f"Invalid input for '{attr}'")
            setattr(challenge, attr, value)

        for attr in ("initial", "minimum", "decay"):
            if (
                challenge.function in DECAY_FUNCTIONS
                and getattr(challenge, attr) is None
            ):
                db.session.rollback()
                raise ChallengeUpdateException(
                    f"Missing '{attr}' but function is {challenge.function}"
                )

        db.session.commit()

        # If the challenge is dynamic we should calculate a new value
        if challenge.function in DECAY_FUNCTIONS:
            return calculate_value(challenge)

        # If we don't support dynamic we just don't do anything
        return challenge

    @classmethod
    def delete(cls, challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        Fails.query.filter_by(challenge_id=challenge.id).delete()
        Solves.query.filter_by(challenge_id=challenge.id).delete()
        Flags.query.filter_by(challenge_id=challenge.id).delete()
        files = ChallengeFiles.query.filter_by(challenge_id=challenge.id).all()
        for f in files:
            delete_file(f.id)
        ChallengeFiles.query.filter_by(challenge_id=challenge.id).delete()
        Tags.query.filter_by(challenge_id=challenge.id).delete()
        Hints.query.filter_by(challenge_id=challenge.id).delete()
        Challenges.query.filter_by(id=challenge.id).delete()
        cls.challenge_model.query.filter_by(id=challenge.id).delete()
        db.session.commit()

    @classmethod
    def attempt(cls, challenge, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()

        flags = Flags.query.filter_by(challenge_id=challenge.id).all()

        if challenge.logic == "any":
            return challenge_attempt_any(submission, challenge, flags)
        elif challenge.logic == "all":
            return challenge_attempt_all(submission, challenge, flags)
        elif challenge.logic == "team":
            return challenge_attempt_team(submission, challenge, flags)
        else:
            return challenge_attempt_any(submission, challenge, flags)

    @classmethod
    def partial(cls, user, team, challenge, request):
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        partial = Partials(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(req=request),
            provided=submission,
        )
        db.session.add(partial)
        db.session.commit()

    @classmethod
    def solve(cls, user, team, challenge, request):
        """
        This method is used to insert Solves into the database in order to mark a challenge as solved.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        solve = Solves(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(req=request),
            provided=submission,
        )
        db.session.add(solve)
        db.session.commit()

        # If the challenge is dynamic we should calculate a new value
        if challenge.function in DECAY_FUNCTIONS:
            calculate_value(challenge)

    @classmethod
    def fail(cls, user, team, challenge, request):
        """
        This method is used to insert Fails into the database in order to mark an answer incorrect.

        :param team: The Team object from the database
        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return:
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()
        wrong = Fails(
            user_id=user.id,
            team_id=team.id if team else None,
            challenge_id=challenge.id,
            ip=get_ip(request),
            provided=submission,
        )
        db.session.add(wrong)
        db.session.commit()


class CTFdStandardChallenge(BaseChallenge):
    id = "standard"  # Unique identifier used to register challenges
    name = "standard"  # Name of a challenge type
    templates = {  # Templates used for each aspect of challenge editing & viewing
        "create": "/plugins/challenges/assets/create.html",
        "update": "/plugins/challenges/assets/update.html",
        "view": "/plugins/challenges/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/challenges/assets/create.js",
        "update": "/plugins/challenges/assets/update.js",
        "view": "/plugins/challenges/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/challenges/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "standard", __name__, template_folder="templates", static_folder="assets"
    )
    challenge_model = Challenges


def get_chal_class(class_id):
    """
    Utility function used to get the corresponding class from a class ID.

    :param class_id: String representing the class ID
    :return: Challenge class
    """
    cls = CHALLENGE_CLASSES.get(class_id)
    if cls is None:
        raise KeyError
    return cls


"""
Global dictionary used to hold all the Challenge Type classes used by CTFd. Insert into this dictionary to register
your Challenge Type.
"""
CHALLENGE_CLASSES = {"standard": CTFdStandardChallenge}


def load(app):
    register_plugin_assets_directory(app, base_path="/plugins/challenges/assets/")
