from marshmallow import validate
from marshmallow.exceptions import ValidationError
from marshmallow_sqlalchemy import field_for

from CTFd.models import Challenges, ma


class ChallengeRequirementsValidator(validate.Validator):
    default_message = "Error parsing challenge requirements"

    def __init__(self, error=None):
        self.error = error or self.default_message

    def __call__(self, value):
        if isinstance(value, dict) is False:
            raise ValidationError(self.default_message)

        prereqs = value.get("prerequisites", [])
        if all(prereqs) is False:
            raise ValidationError(
                "Challenge requirements cannot have a null prerequisite"
            )

        return value


class ChallengeSchema(ma.ModelSchema):
    class Meta:
        model = Challenges
        include_fk = True
        dump_only = ("id",)

    name = field_for(
        Challenges,
        "name",
        validate=[
            validate.Length(
                min=0,
                max=80,
                error="Challenge could not be saved. Challenge name too long",
            )
        ],
    )

    category = field_for(
        Challenges,
        "category",
        validate=[
            validate.Length(
                min=0,
                max=80,
                error="Challenge could not be saved. Challenge category too long",
            )
        ],
    )

    description = field_for(
        Challenges,
        "description",
        allow_none=True,
        validate=[
            validate.Length(
                min=0,
                max=65535,
                error="Challenge could not be saved. Challenge description too long",
            )
        ],
    )

    requirements = field_for(
        Challenges, "requirements", validate=[ChallengeRequirementsValidator()],
    )
