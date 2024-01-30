from flask_babel import lazy_gettext as _l
from wtforms import BooleanField, PasswordField, SelectField, StringField
from wtforms.fields.html5 import EmailField, URLField
from wtforms.validators import InputRequired

from CTFd.forms import BaseForm
from CTFd.forms.fields import SubmitField
from CTFd.models import Brackets, TeamFieldEntries, TeamFields
from CTFd.utils.countries import SELECT_COUNTRIES_LIST
from CTFd.utils.user import get_current_team


def build_team_bracket_field(form_cls, value=None):
    field = getattr(form_cls, "bracket_id", None)  # noqa B009
    if field:
        field.field_type = "select"
        field.process_data(value)
        return [field]
    else:
        return []


def attach_team_bracket_field(form_cls):
    brackets = Brackets.query.filter_by(type="teams").all()
    if brackets:
        choices = [("", "")] + [
            (bracket.id, f"{bracket.name} - {bracket.description}")
            for bracket in brackets
        ]
        select_field = SelectField(
            "Bracket",
            description="Competition bracket for your team",
            choices=choices,
            validators=[InputRequired()],
        )
        setattr(form_cls, "bracket_id", select_field)  # noqa B010


def build_custom_team_fields(
    form_cls,
    include_entries=False,
    fields_kwargs=None,
    field_entries_kwargs=None,
    blacklisted_items=(),
):
    if fields_kwargs is None:
        fields_kwargs = {}
    if field_entries_kwargs is None:
        field_entries_kwargs = {}

    fields = []
    new_fields = TeamFields.query.filter_by(**fields_kwargs).all()
    user_fields = {}

    # Only include preexisting values if asked
    if include_entries is True:
        for f in TeamFieldEntries.query.filter_by(**field_entries_kwargs).all():
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


def attach_custom_team_fields(form_cls, **kwargs):
    new_fields = TeamFields.query.filter_by(**kwargs).all()
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


class TeamJoinForm(BaseForm):
    name = StringField(_l("Team Name"), validators=[InputRequired()])
    password = PasswordField(_l("Team Password"), validators=[InputRequired()])
    submit = SubmitField(_l("Join"))


def TeamRegisterForm(*args, **kwargs):
    class _TeamRegisterForm(BaseForm):
        name = StringField(_l("Team Name"), validators=[InputRequired()])
        password = PasswordField(_l("Team Password"), validators=[InputRequired()])
        submit = SubmitField(_l("Create"))

        @property
        def extra(self):
            return build_custom_team_fields(
                self, include_entries=False, blacklisted_items=()
            ) + build_team_bracket_field(self)

    attach_custom_team_fields(_TeamRegisterForm)
    attach_team_bracket_field(_TeamRegisterForm)
    return _TeamRegisterForm(*args, **kwargs)


def TeamSettingsForm(*args, **kwargs):
    class _TeamSettingsForm(BaseForm):
        name = StringField(
            _l("Team Name"),
            description=_l("Your team's public name shown to other competitors"),
        )
        password = PasswordField(
            _l("New Team Password"), description=_l("Set a new team join password")
        )
        confirm = PasswordField(
            _l("Confirm Current Team Password"),
            description=_l(
                "Provide your current team password (or your password) to update your team's password"
            ),
        )
        affiliation = StringField(
            _l("Affiliation"),
            description=_l(
                "Your team's affiliation publicly shown to other competitors"
            ),
        )
        website = URLField(
            _l("Website"),
            description=_l("Your team's website publicly shown to other competitors"),
        )
        country = SelectField(
            _l("Country"),
            choices=SELECT_COUNTRIES_LIST,
            description=_l("Your team's country publicly shown to other competitors"),
        )
        submit = SubmitField(_l("Submit"))

        @property
        def extra(self):
            fields_kwargs = _TeamSettingsForm.get_field_kwargs()
            return build_custom_team_fields(
                self,
                include_entries=True,
                fields_kwargs=fields_kwargs,
                field_entries_kwargs={"team_id": self.obj.id},
            )

        def get_field_kwargs():
            team = get_current_team()
            field_kwargs = {"editable": True}
            if team.filled_all_required_fields is False:
                # Show all fields
                field_kwargs = {}
            return field_kwargs

        def __init__(self, *args, **kwargs):
            """
            Custom init to persist the obj parameter to the rest of the form
            """
            super().__init__(*args, **kwargs)
            obj = kwargs.get("obj")
            if obj:
                self.obj = obj

    field_kwargs = _TeamSettingsForm.get_field_kwargs()
    attach_custom_team_fields(_TeamSettingsForm, **field_kwargs)

    return _TeamSettingsForm(*args, **kwargs)


class TeamCaptainForm(BaseForm):
    # Choices are populated dynamically at form creation time
    captain_id = SelectField(
        _l("Team Captain"), choices=[], validators=[InputRequired()]
    )
    submit = SubmitField("Submit")


class TeamSearchForm(BaseForm):
    field = SelectField(
        "Search Field",
        choices=[
            ("name", "Name"),
            ("id", "ID"),
            ("affiliation", "Affiliation"),
            ("website", "Website"),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField("Parameter", validators=[InputRequired()])
    submit = SubmitField("Search")


class PublicTeamSearchForm(BaseForm):
    field = SelectField(
        _l("Search Field"),
        choices=[
            ("name", _l("Name")),
            ("affiliation", _l("Affiliation")),
            ("website", _l("Website")),
        ],
        default="name",
        validators=[InputRequired()],
    )
    q = StringField(_l("Parameter"), validators=[InputRequired()])
    submit = SubmitField(_l("Search"))


class TeamBaseForm(BaseForm):
    name = StringField(_l("Team Name"), validators=[InputRequired()])
    email = EmailField(_l("Email"))
    password = PasswordField(_l("Password"))
    website = URLField(_l("Website"))
    affiliation = StringField(_l("Affiliation"))
    country = SelectField(_l("Country"), choices=SELECT_COUNTRIES_LIST)
    hidden = BooleanField(_l("Hidden"))
    banned = BooleanField(_l("Banned"))
    submit = SubmitField(_l("Submit"))


def TeamCreateForm(*args, **kwargs):
    class _TeamCreateForm(TeamBaseForm):
        pass

        @property
        def extra(self):
            return build_custom_team_fields(
                self, include_entries=False
            ) + build_team_bracket_field(self)

    attach_custom_team_fields(_TeamCreateForm)
    attach_team_bracket_field(_TeamCreateForm)

    return _TeamCreateForm(*args, **kwargs)


def TeamEditForm(*args, **kwargs):
    class _TeamEditForm(TeamBaseForm):
        pass

        @property
        def extra(self):
            return build_custom_team_fields(
                self,
                include_entries=True,
                fields_kwargs=None,
                field_entries_kwargs={"team_id": self.obj.id},
            ) + build_team_bracket_field(self, value=self.obj.bracket_id)

        def __init__(self, *args, **kwargs):
            """
            Custom init to persist the obj parameter to the rest of the form
            """
            super().__init__(*args, **kwargs)
            obj = kwargs.get("obj")
            if obj:
                self.obj = obj

    attach_custom_team_fields(_TeamEditForm)
    attach_team_bracket_field(_TeamEditForm)

    return _TeamEditForm(*args, **kwargs)


class TeamInviteForm(BaseForm):
    link = URLField(_l("Invite Link"))


class TeamInviteJoinForm(BaseForm):
    submit = SubmitField(_l("Join"))
