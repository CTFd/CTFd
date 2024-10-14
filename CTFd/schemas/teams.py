from marshmallow import ValidationError, post_dump, pre_load, validate
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import field_for
from sqlalchemy.orm import load_only

from CTFd.models import Brackets, TeamFieldEntries, TeamFields, Teams, Users, ma
from CTFd.schemas.fields import TeamFieldEntriesSchema
from CTFd.utils import get_config, string_types
from CTFd.utils.crypto import verify_password
from CTFd.utils.user import get_current_team, get_current_user, is_admin
from CTFd.utils.validators import validate_country_code


class TeamSchema(ma.ModelSchema):
    class Meta:
        model = Teams
        include_fk = True
        dump_only = ("id", "oauth_id", "created", "members")
        load_only = ("password",)

    name = field_for(
        Teams,
        "name",
        required=True,
        allow_none=False,
        validate=[
            validate.Length(min=1, max=128, error="Team names must not be empty")
        ],
    )
    email = field_for(
        Teams,
        "email",
        allow_none=False,
        validate=validate.Email("Emails must be a properly formatted email address"),
    )
    password = field_for(Teams, "password", required=True, allow_none=False)
    website = field_for(
        Teams,
        "website",
        validate=[
            # This is a dirty hack to let website accept empty strings so you can remove your website
            lambda website: validate.URL(
                error="Websites must be a proper URL starting with http or https",
                schemes={"http", "https"},
            )(website)
            if website
            else True
        ],
    )
    country = field_for(Teams, "country", validate=[validate_country_code])
    bracket_id = field_for(Teams, "bracket_id")
    fields = Nested(
        TeamFieldEntriesSchema, partial=True, many=True, attribute="field_entries"
    )

    @pre_load
    def validate_name(self, data):
        name = data.get("name")
        if name is None:
            return
        name = name.strip()

        existing_team = Teams.query.filter_by(name=name).first()
        current_team = get_current_team()
        # Admins should be able to patch anyone but they cannot cause a collision.
        if is_admin():
            team_id = int(data.get("id", 0))
            if team_id:
                if existing_team and existing_team.id != team_id:
                    raise ValidationError(
                        "Team name has already been taken", field_names=["name"]
                    )
            else:
                # If there's no Team ID it means that the admin is creating a team with no ID.
                if existing_team:
                    if current_team:
                        if current_team.id != existing_team.id:
                            raise ValidationError(
                                "Team name has already been taken", field_names=["name"]
                            )
                    else:
                        raise ValidationError(
                            "Team name has already been taken", field_names=["name"]
                        )
        else:
            # We need to allow teams to edit themselves and allow the "conflict"
            if data["name"] == current_team.name:
                return data
            else:
                name_changes = get_config("name_changes", default=True)
                if bool(name_changes) is False:
                    raise ValidationError(
                        "Name changes are disabled", field_names=["name"]
                    )

                if existing_team:
                    raise ValidationError(
                        "Team name has already been taken", field_names=["name"]
                    )

    @pre_load
    def validate_email(self, data):
        email = data.get("email")
        if email is None:
            return

        existing_team = Teams.query.filter_by(email=email).first()
        if is_admin():
            team_id = data.get("id")
            if team_id:
                if existing_team and existing_team.id != team_id:
                    raise ValidationError(
                        "Email address has already been used", field_names=["email"]
                    )
            else:
                if existing_team:
                    raise ValidationError(
                        "Email address has already been used", field_names=["email"]
                    )
        else:
            current_team = get_current_team()
            if email == current_team.email:
                return data
            else:
                if existing_team:
                    raise ValidationError(
                        "Email address has already been used", field_names=["email"]
                    )

    @pre_load
    def validate_password_confirmation(self, data):
        password = data.get("password")
        confirm = data.get("confirm")

        if is_admin():
            pass
        else:
            current_team = get_current_team()
            current_user = get_current_user()

            if current_team.captain_id != current_user.id:
                raise ValidationError(
                    "Only the captain can change the team password",
                    field_names=["captain_id"],
                )

            if current_team.password is None:
                return

            if password and (bool(confirm) is False):
                raise ValidationError(
                    "Please confirm your current password", field_names=["confirm"]
                )

            if password and confirm:
                test_team = verify_password(
                    plaintext=confirm, ciphertext=current_team.password
                )
                test_captain = verify_password(
                    plaintext=confirm, ciphertext=current_user.password
                )
                if test_team is True or test_captain is True:
                    return data
                else:
                    raise ValidationError(
                        "Your previous password is incorrect", field_names=["confirm"]
                    )
            else:
                data.pop("password", None)
                data.pop("confirm", None)

    @pre_load
    def validate_captain_id(self, data):
        captain_id = data.get("captain_id")
        if captain_id is None:
            return

        if is_admin():
            team_id = data.get("id")
            if team_id:
                target_team = Teams.query.filter_by(id=team_id).first()
            else:
                target_team = get_current_team()
            captain = Users.query.filter_by(id=captain_id).first()
            if captain in target_team.members:
                return
            else:
                raise ValidationError("Invalid Captain ID", field_names=["captain_id"])
        else:
            current_team = get_current_team()
            current_user = get_current_user()
            if current_team.captain_id == current_user.id:
                captain = Users.query.filter_by(id=captain_id).first()
                if captain in current_team.members:
                    return
                else:
                    raise ValidationError(
                        "Only team members can be promoted to captain",
                        field_names=["captain_id"],
                    )
            else:
                raise ValidationError(
                    "Only the captain can change team captain",
                    field_names=["captain_id"],
                )

    @pre_load
    def validate_bracket_id(self, data):
        bracket_id = data.get("bracket_id")
        if is_admin():
            bracket = Brackets.query.filter_by(id=bracket_id).first()
            if bracket is None:
                ValidationError(
                    "Please provide a valid bracket id", field_names=["bracket_id"]
                )
        else:
            current_team = get_current_team()
            # Teams are not allowed to switch their bracket
            if bracket_id is None:
                # Remove bracket_id and short circuit processing
                data.pop("bracket_id", None)
                return
            if (
                current_team.bracket_id == int(bracket_id)
                or current_team.bracket_id is None
            ):
                bracket = Brackets.query.filter_by(id=bracket_id, type="teams").first()
                if bracket is None:
                    ValidationError(
                        "Please provide a valid bracket id", field_names=["bracket_id"]
                    )
            else:
                raise ValidationError(
                    "Please contact an admin to change your bracket",
                    field_names=["bracket_id"],
                )

    @pre_load
    def validate_fields(self, data):
        """
        This validator is used to only allow users to update the field entry for their user.
        It's not possible to exclude it because without the PK Marshmallow cannot load the right instance
        """
        fields = data.get("fields")
        if fields is None:
            return

        current_team = get_current_team()

        if is_admin():
            team_id = data.get("id")
            if team_id:
                target_team = Teams.query.filter_by(id=data["id"]).first()
            else:
                target_team = current_team

            # We are editting an existing
            if self.view == "admin" and self.instance:
                target_team = self.instance
                provided_ids = []
                for f in fields:
                    f.pop("id", None)
                    field_id = f.get("field_id")

                    # # Check that we have an existing field for this. May be unnecessary b/c the foriegn key should enforce
                    field = TeamFields.query.filter_by(id=field_id).first_or_404()

                    # Get the existing field entry if one exists
                    entry = TeamFieldEntries.query.filter_by(
                        field_id=field.id, team_id=target_team.id
                    ).first()
                    if entry:
                        f["id"] = entry.id
                        provided_ids.append(entry.id)

                # Extremely dirty hack to prevent deleting previously provided data.
                # This needs a better soln.
                entries = (
                    TeamFieldEntries.query.options(load_only("id"))
                    .filter_by(team_id=target_team.id)
                    .all()
                )
                for entry in entries:
                    if entry.id not in provided_ids:
                        fields.append({"id": entry.id})
        else:
            provided_ids = []
            for f in fields:
                # Remove any existing set
                f.pop("id", None)
                field_id = f.get("field_id")
                value = f.get("value")

                # # Check that we have an existing field for this. May be unnecessary b/c the foriegn key should enforce
                field = TeamFields.query.filter_by(id=field_id).first_or_404()

                # Get the existing field entry if one exists
                entry = TeamFieldEntries.query.filter_by(
                    field_id=field.id, team_id=current_team.id
                ).first()

                if field.required is True:
                    if isinstance(value, str):
                        if value.strip() == "":
                            raise ValidationError(
                                f"Field '{field.name}' is required",
                                field_names=["fields"],
                            )

                if field.editable is False and entry is not None:
                    raise ValidationError(
                        f"Field '{field.name}' cannot be editted",
                        field_names=["fields"],
                    )

                if entry:
                    f["id"] = entry.id
                    provided_ids.append(entry.id)

            # Extremely dirty hack to prevent deleting previously provided data.
            # This needs a better soln.
            entries = (
                TeamFieldEntries.query.options(load_only("id"))
                .filter_by(team_id=current_team.id)
                .all()
            )
            for entry in entries:
                if entry.id not in provided_ids:
                    fields.append({"id": entry.id})

    @post_dump
    def process_fields(self, data):
        """
        Handle permissions levels for fields.
        This is post_dump to manipulate JSON instead of the raw db object

        Admins can see all fields.
        Users (self) can see their edittable and public fields
        Public (user) can only see public fields
        """
        # Gather all possible fields
        removed_field_ids = []
        fields = TeamFields.query.all()

        # Select fields for removal based on current view and properties of the field
        for field in fields:
            if self.view == "user":
                if field.public is False:
                    removed_field_ids.append(field.id)
            elif self.view == "self":
                if field.editable is False and field.public is False:
                    removed_field_ids.append(field.id)

        # Rebuild fuilds
        fields = data.get("fields")
        if fields:
            data["fields"] = [
                field for field in fields if field["field_id"] not in removed_field_ids
            ]

    views = {
        "user": [
            "website",
            "name",
            "country",
            "affiliation",
            "bracket_id",
            "members",
            "id",
            "oauth_id",
            "captain_id",
            "fields",
        ],
        "self": [
            "website",
            "name",
            "email",
            "country",
            "affiliation",
            "bracket_id",
            "members",
            "id",
            "oauth_id",
            "password",
            "captain_id",
            "fields",
        ],
        "admin": [
            "website",
            "name",
            "created",
            "country",
            "banned",
            "email",
            "affiliation",
            "secret",
            "bracket_id",
            "members",
            "hidden",
            "id",
            "oauth_id",
            "password",
            "captain_id",
            "fields",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view
        self.view = view

        super(TeamSchema, self).__init__(*args, **kwargs)
