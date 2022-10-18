from marshmallow import validate, ValidationError
from marshmallow_sqlalchemy import field_for

from CTFd.models import Users, ma
from CTFd.utils import string_types
from CTFd.utils.validators import validate_country_code
from CTFd.plugins.migrations import upgrade
from CTFd.plugins.csaw.utils import validate_csaw_region, validate_csaw_bracket


def validate_email(email):
    if email == '':
        return True
    return validate.Email("Emails must be a properly formatted email address")(email)

def validate_team_count(team_count):
    try:
        n = int(team_count)
    except ValueError:
        raise ValidationError("Invalid Team Count")
    if not (0 < n <= 20):
        raise ValidationError("Invalid Team Count")

class CSAWSchema(ma.ModelSchema):
    class Meta:
        model = Users
        include_fk = True
        dump_only = ("id", "oauth_id", "created")
        load_only = ("password",)

    # Member 1
    member_1_name = field_for(
        Users, "member_1_name", required=False, allow_none=False,
        validate=[
            validate.Length(min=0, max=128, error="User names must not be empty")
        ],
    )
    member_1_email = field_for(
        Users, "member_1_email", required=False, allow_none=False,
        validate=[
            validate_email,
            validate.Length(min=0, max=128, error="Emails must not be empty"),
        ],
    )
    member_1_school = field_for(
        Users, "member_1_school", required=False, allow_none=False,
        validate=[
            validate.Length(min=0, max=128, error="User names must not be empty")
        ],
    )

    # Member 2
    member_2_name = field_for(
        Users, "member_2_name", required=False, allow_none=False,
        validate=[
            validate.Length(min=0, max=128, error="User names must not be empty")
        ],
    )
    member_2_email = field_for(
        Users, "member_2_email", required=False, allow_none=False,
        validate=[
            validate_email,
            validate.Length(min=0, max=128, error="Emails must not be empty"),
        ],
    )
    member_2_school = field_for(
        Users, "member_2_school", required=False, allow_none=False,
        validate=[
            validate.Length(min=0, max=128, error="User names must not be empty")
        ],
    )

    # Member 3
    member_3_name = field_for(
        Users, "member_3_name", required=False, allow_none=False,
        validate=[
            validate.Length(min=0, max=128, error="User names must not be empty")
        ],
    )
    member_3_email = field_for(
        Users, "member_3_email", required=False, allow_none=False,
        validate=[
            validate_email,
            validate.Length(min=0, max=128, error="Emails must not be empty"),
        ],
    )
    member_3_school = field_for(
        Users, "member_3_school", required=False, allow_none=False,
        validate=[
            validate.Length(min=0, max=128, error="User names must not be empty")
        ],
    )

    # Member 4
    member_4_name = field_for(
        Users, "member_4_name", required=False, allow_none=False,
        validate=[
            validate.Length(min=0, max=128, error="User names must not be empty")
        ],
    )
    member_4_email = field_for(
        Users, "member_4_email", required=False, allow_none=False,
        validate=[
            validate_email,
            validate.Length(min=0, max=128, error="Emails must not be empty"),
        ],
    )
    member_4_school = field_for(
        Users, "member_4_school", required=False, allow_none=False,
        validate=[
            validate.Length(min=0, max=128, error="User names must not be empty")
        ],
    )

    country = field_for(Users, "country", validate=[validate_country_code])
    bracket = field_for(Users, "bracket", validate=[validate_csaw_bracket])
    region = field_for(Users, "region", validate=[validate_csaw_region])
    team_count = field_for(Users, "team_count", validate=[validate_team_count])

    views = {
        "self": [
            "member_1_name",
            "member_1_email",
            "member_1_school",

            "member_2_name",
            "member_2_email",
            "member_2_school",

            "member_3_name",
            "member_3_email",
            "member_3_school",

            "member_4_name",
            "member_4_email",
            "member_4_school",

            "country",
            "bracket",
            "region",
            "team_count",
        ],
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view
        self.view = view

        super(CSAWSchema, self).__init__(*args, **kwargs)

def load(app):
    upgrade(plugin_name="csaw")