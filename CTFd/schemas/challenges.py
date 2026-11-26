from marshmallow import fields, validate, validates
from marshmallow.exceptions import ValidationError
from marshmallow_sqlalchemy import field_for

from CTFd.models import Challenges, Modules, ma


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

    position = field_for(
        Challenges,
        "position",
        validate=[
            validate.Range(
                min=0,
                max=32767,
                error="Challenge could not be saved. Challenge position is invalid",
            )
        ],
    )

    max_attempts = field_for(
        Challenges,
        "max_attempts",
        allow_none=False,
        error_messages={
            "null": "Challenge could not be saved. Max attempts cannot be null, use 0 for unlimited attempts"
        },
        validate=[
            validate.Range(
                min=0,
                error="Challenge could not be saved. Max attempts cannot be negative, use 0 for unlimited attempts",
            )
        ],
    )

    requirements = field_for(
        Challenges,
        "requirements",
        validate=[ChallengeRequirementsValidator()],
    )

    module_ids = fields.List(fields.Integer(), allow_none=True)

    @validates("module_ids")
    def validate_module_ids(self, value):
        ids = {i for i in (value or []) if isinstance(i, int)}
        if not ids:
            return

        found = {
            m.id
            for m in Modules.query.with_entities(Modules.id).filter(Modules.id.in_(ids))
        }
        missing = sorted(ids - found)
        if missing:
            raise ValidationError(
                "Invalid module id(s): {}".format(", ".join(map(str, missing)))
            )
