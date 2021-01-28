from marshmallow import ValidationError, pre_load

from CTFd.models import Challenges, ma


class ChallengeSchema(ma.ModelSchema):
    class Meta:
        model = Challenges
        include_fk = True
        dump_only = ("id",)

    @pre_load
    def validate_name(self, data):
        name = data.get("name", "")
        if len(name) > 80:
            raise ValidationError(
                "Challenge could not be saved. Challenge name too long",
                field_names=["name"],
            )

    @pre_load
    def validate_category(self, data):
        category = data.get("category", "")
        if len(category) > 80:
            raise ValidationError(
                "Challenge could not be saved. Challenge category too long",
                field_names=["category"],
            )

    @pre_load
    def validate_description(self, data):
        description = data.get("description", "")
        if len(description) >= 65536:
            raise ValidationError(
                "Challenge could not be saved. Challenge description is too long.",
                field_names=["description"],
            )
