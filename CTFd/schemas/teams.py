from marshmallow import ValidationError, pre_load, validate
from marshmallow_sqlalchemy import field_for

from CTFd.models import Teams, Users, ma
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

            if password and (bool(confirm) is False):
                raise ValidationError(
                    "Please confirm your current password", field_names=["confirm"]
                )

            if password and confirm:
                test = verify_password(
                    plaintext=confirm, ciphertext=current_team.password
                )
                if test is True:
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
                return
            else:
                raise ValidationError(
                    "Only the captain can change team captain",
                    field_names=["captain_id"],
                )

    views = {
        "user": [
            "website",
            "name",
            "country",
            "affiliation",
            "bracket",
            "members",
            "id",
            "oauth_id",
            "captain_id",
        ],
        "self": [
            "website",
            "name",
            "email",
            "country",
            "affiliation",
            "bracket",
            "members",
            "id",
            "oauth_id",
            "password",
            "captain_id",
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
            "bracket",
            "members",
            "hidden",
            "id",
            "oauth_id",
            "password",
            "captain_id",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(TeamSchema, self).__init__(*args, **kwargs)
