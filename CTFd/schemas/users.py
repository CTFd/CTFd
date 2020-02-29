from marshmallow import ValidationError, pre_load, validate
from marshmallow_sqlalchemy import field_for

from CTFd.models import Users, ma
from CTFd.utils import get_config, string_types
from CTFd.utils.crypto import verify_password
from CTFd.utils.email import check_email_is_whitelisted
from CTFd.utils.user import get_current_user, is_admin
from CTFd.utils.validators import validate_country_code


class UserSchema(ma.ModelSchema):
    class Meta:
        model = Users
        include_fk = True
        dump_only = ("id", "oauth_id", "created")
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
    country = field_for(Users, "country", validate=[validate_country_code])
    password = field_for(Users, "password")

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
                        "Only email addresses under {domains} may register".format(
                            domains=get_config("domain_whitelist")
                        ),
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

    views = {
        "user": [
            "website",
            "name",
            "country",
            "affiliation",
            "bracket",
            "id",
            "oauth_id",
        ],
        "self": [
            "website",
            "name",
            "email",
            "country",
            "affiliation",
            "bracket",
            "id",
            "oauth_id",
            "password",
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
            "hidden",
            "id",
            "oauth_id",
            "password",
            "type",
            "verified",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(UserSchema, self).__init__(*args, **kwargs)
