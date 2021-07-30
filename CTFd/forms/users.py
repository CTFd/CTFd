from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from CTFd.constants.config import Configs
from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import UserFieldEntries, UserFields
from CTFd.utils.countries import SELECT_COUNTRIES_LIST


def build_custom_user_fields(
    form_cls,
    include_entries=False,
    fields_kwargs=None,
    field_entries_kwargs=None,
    blacklisted_items=("affiliation", "website"),
):
    """
    Function used to reinject values back into forms for accessing by themes
    """
    if fields_kwargs is None:
        fields_kwargs = {}
    if field_entries_kwargs is None:
        field_entries_kwargs = {}

    fields = []
    new_fields = UserFields.query.filter_by(**fields_kwargs).all()
    user_fields = {}

    # Only include preexisting values if asked
    if include_entries is True:
        for f in UserFieldEntries.query.filter_by(**field_entries_kwargs).all():
            user_fields[f.field_id] = f.value

    for field in new_fields:
        if field.name.lower() in blacklisted_items:
            continue

        form_field = getattr(form_cls, f"fields[{field.id}]")

        # Add the field_type to the field so we know how to render it
        form_field.field_type = field.field_type

        # Only include preexisting values if asked
        if include_entries is True:
            initial = user_fields.get(field.id, "")
            form_field.data = initial
            if form_field.render_kw:
                form_field.render_kw["data-initial"] = initial
            else:
                form_field.render_kw = {"data-initial": initial}

        fields.append(form_field)
    return fields


def attach_custom_user_fields(form_cls, **kwargs):
    """
    Function used to attach form fields to wtforms.
    Not really a great solution but is approved by wtforms.

    https://wtforms.readthedocs.io/en/2.3.x/specific_problems/#dynamic-form-composition
    """
    new_fields = UserFields.query.filter_by(**kwargs).all()
    for field in new_fields:
        validators = []
        if field.required:
            validators.append(InputRequired())

        if field.field_type == "text":
            input_field = StringField(
                field.name, description=field.description, validators=validators
            )
        elif field.field_type == "boolean":
            input_field = BooleanField(
                field.name, description=field.description, validators=validators
            )

        setattr(form_cls, f"fields[{field.id}]", input_field)


def build_registration_code_field(form_cls):
    """
    Build the appropriate field so we can render it via the extra property.
    Add field_type so Jinja knows how to render it.
    """
    if Configs.registration_code:
        field = getattr(form_cls, "registration_code")  # noqa B009
        field.field_type = "text"
        return [field]
    else:
        return []


def attach_registration_code_field(form_cls):
    """
    If we have a registration code required, we attach it to the form similar
    to attach_custom_user_fields
    """
    if Configs.registration_code:
        setattr(  # noqa B010
            form_cls,
            "registration_code",
            StringField(
                "Registration Code",
                description="Registration code required to create account",
                validators=[InputRequired()],
            ),
        )


class UserSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("id", "ID"),
            ("email", "Email"),
            ("affiliation", "Affiliation"),
            ("website", "Website"),
            ("ip", "IP Address"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class PublicUserSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("affiliation", "Affiliation"),
            ("website", "Website"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class UserBaseForm(BaseForm):
    name = StringField("User Name", validators=[InputRequired()])
    email = EmailField("Email", validators=[InputRequired()])
    password = PasswordField("Password")
    website = StringField("Website")
    affiliation = StringField("Affiliation")
    country = SelectField("Country", choices=SELECT_COUNTRIES_LIST)
    type = SelectField("Type", choices=[("user", "User"), ("admin", "Admin")])
    verified = BooleanField("Verified")
    hidden = BooleanField("Hidden")
    banned = BooleanField("Banned")
    submit = SubmitField("Submit")


def UserEditForm(*args, **kwargs):
    class _UserEditForm(UserBaseForm):
        pass

        @property
        def extra(self):
            return build_custom_user_fields(
                self,
                include_entries=True,
                fields_kwargs=None,
                field_entries_kwargs={"user_id": self.obj.id},
            )

        def __init__(self, *args, **kwargs):
            """
            Custom init to persist the obj parameter to the rest of the form
            """
            super().__init__(*args, **kwargs)
            obj = kwargs.get("obj")
            if obj:
                self.obj = obj

    attach_custom_user_fields(_UserEditForm)

    return _UserEditForm(*args, **kwargs)


def UserCreateForm(*args, **kwargs):
    class _UserCreateForm(UserBaseForm):
        notify = BooleanField("Email account credentials to user", default=True)

        @property
        def extra(self):
            return build_custom_user_fields(self, include_entries=False)

    attach_custom_user_fields(_UserCreateForm)

    return _UserCreateForm(*args, **kwargs)
