from marshmallow import ValidationError, post_dump, pre_load, validate
from marshmallow.fields import Nested
from marshmallow_sqlalchemy import field_for
from sqlalchemy.orm import load_only

from CTFd.models import Brackets, UserFieldEntries, UserFields, Users, ma
from CTFd.schemas.fields import UserFieldEntriesSchema
from CTFd.utils import get_config, string_types
from CTFd.utils.crypto import verify_password
from CTFd.utils.email import check_email_is_whitelisted
from CTFd.utils.user import get_current_user, is_admin
from CTFd.utils.validators import validate_country_code, validate_language


class UserSchema(ma.ModelSchema):
    class Meta:
        model = Users
        include_fk = True
        dump_only = ("id", "oauth_id", "created", "team_id")
        load_only = ("password",)

    name = field_for(
        Users,
        "name",
        required=True,
        allow_none=False,
        validate=[
            validate.Length(min=1, max=128, error="User names must not be empty")
        ],
    )
    email = field_for(
        Users,
        "email",
        allow_none=False,
        validate=[
            validate.Email("Emails must be a properly formatted email address"),
            validate.Length(min=1, max=128, error="Emails must not be empty"),
        ],
    )
    website = field_for(
        Users,
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
    language = field_for(Users, "language", validate=[validate_language])
    country = field_for(Users, "country", validate=[validate_country_code])
    password = field_for(Users, "password", required=True, allow_none=False)
    bracket_id = field_for(Users, "bracket_id")
    fields = Nested(
        UserFieldEntriesSchema, partial=True, many=True, attribute="field_entries"
    )

    @pre_load
    def validate_name(self, data):
        name = data.get("name")
        if name is None:
            return
        name = name.strip()

        existing_user = Users.query.filter_by(name=name).first()
        current_user = get_current_user()
        if is_admin():
            user_id = data.get("id")
            if user_id:
                if existing_user and existing_user.id != user_id:
                    raise ValidationError(
                        "User name has already been taken", field_names=["name"]
                    )
            else:
                if existing_user:
                    if current_user:
                        if current_user.id != existing_user.id:
                            raise ValidationError(
                                "User name has already been taken", field_names=["name"]
                            )
                    else:
                        raise ValidationError(
                            "User name has already been taken", field_names=["name"]
                        )
        else:
            if name == current_user.name:
                return data
            else:
                name_changes = get_config("name_changes", default=True)
                if bool(name_changes) is False:
                    raise ValidationError(
                        "Name changes are disabled", field_names=["name"]
                    )
                if existing_user:
                    raise ValidationError(
                        "User name has already been taken", field_names=["name"]
                    )

    @pre_load
    def validate_email(self, data):
        email = data.get("email")
        if email is None:
            return
        email = email.strip()

        existing_user = Users.query.filter_by(email=email).first()
        current_user = get_current_user()
        if is_admin():
            user_id = data.get("id")
            if user_id:
                if existing_user and existing_user.id != user_id:
                    raise ValidationError(
                        "Email address has already been used", field_names=["email"]
                    )
            else:
                if existing_user:
                    if current_user:
                        if current_user.id != existing_user.id:
                            raise ValidationError(
                                "Email address has already been used",
                                field_names=["email"],
                            )
                    else:
                        raise ValidationError(
                            "Email address has already been used", field_names=["email"]
                        )
        else:
            if email == current_user.email:
                return data
            else:
                confirm = data.get("confirm")

                if bool(confirm) is False:
                    raise ValidationError(
                        "Please confirm your current password", field_names=["confirm"]
                    )

                test = verify_password(
                    plaintext=confirm, ciphertext=current_user.password
                )
                if test is False:
                    raise ValidationError(
                        "Your previous password is incorrect", field_names=["confirm"]
                    )

                if existing_user:
                    raise ValidationError(
                        "Email address has already been used", field_names=["email"]
                    )
                if check_email_is_whitelisted(email) is False:
                    raise ValidationError(
                        "Email address is not from an allowed domain",
                        field_names=["email"],
                    )
                if get_config("verify_emails"):
                    current_user.verified = False

    @pre_load
    def validate_password_confirmation(self, data):
        password = data.get("password")
        confirm = data.get("confirm")
        target_user = get_current_user()

        if is_admin():
            pass
        else:
            if password and (bool(confirm) is False):
                raise ValidationError(
                    "Please confirm your current password", field_names=["confirm"]
                )

            if target_user.password is None:
                # Prevent password from being set but allow other data through
                data.pop("password", None)
                data.pop("confirm", None)
                return

            if password and confirm:
                test = verify_password(
                    plaintext=confirm, ciphertext=target_user.password
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
    def validate_bracket_id(self, data):
        bracket_id = data.get("bracket_id")
        if bracket_id is None:
            return

        current_user = get_current_user()
        if is_admin():
            bracket = Brackets.query.filter_by(id=bracket_id, type="users").first()
            if bracket is None:
                ValidationError(
                    "Please provide a valid bracket id", field_names=["bracket_id"]
                )
        else:
            if (
                current_user.bracket_id == int(bracket_id)
                or current_user.bracket_id is None
            ):
                bracket = Brackets.query.filter_by(id=bracket_id, type="users").first()
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

        current_user = get_current_user()

        if is_admin():
            user_id = data.get("id")
            if user_id:
                target_user = Users.query.filter_by(id=data["id"]).first()
            else:
                target_user = current_user

            # We are editting an existing user
            if self.view == "admin" and self.instance:
                target_user = self.instance
                provided_ids = []
                for f in fields:
                    f.pop("id", None)
                    field_id = f.get("field_id")

                    # # Check that we have an existing field for this. May be unnecessary b/c the foriegn key should enforce
                    field = UserFields.query.filter_by(id=field_id).first_or_404()

                    # Get the existing field entry if one exists
                    entry = UserFieldEntries.query.filter_by(
                        field_id=field.id, user_id=target_user.id
                    ).first()
                    if entry:
                        f["id"] = entry.id
                        provided_ids.append(entry.id)

                # Extremely dirty hack to prevent deleting previously provided data.
                # This needs a better soln.
                entries = (
                    UserFieldEntries.query.options(load_only("id"))
                    .filter_by(user_id=target_user.id)
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
                field = UserFields.query.filter_by(id=field_id).first_or_404()

                # Get the existing field entry if one exists
                entry = UserFieldEntries.query.filter_by(
                    field_id=field.id, user_id=current_user.id
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
                UserFieldEntries.query.options(load_only("id"))
                .filter_by(user_id=current_user.id)
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
        fields = UserFields.query.all()

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
            "id",
            "oauth_id",
            "fields",
            "team_id",
        ],
        "self": [
            "website",
            "name",
            "email",
            "language",
            "country",
            "affiliation",
            "bracket_id",
            "id",
            "oauth_id",
            "password",
            "fields",
            "team_id",
        ],
        "admin": [
            "website",
            "name",
            "created",
            "country",
            "banned",
            "email",
            "language",
            "affiliation",
            "secret",
            "bracket_id",
            "hidden",
            "id",
            "oauth_id",
            "password",
            "type",
            "verified",
            "fields",
            "team_id",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view
        self.view = view

        super(UserSchema, self).__init__(*args, **kwargs)
