from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load
from marshmallow import validate, ValidationError, pre_load
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Teams
from CTFd.utils.validators import validate_country_code
from CTFd.utils import get_config
from CTFd.utils.user import is_admin, get_current_team
from CTFd.utils.countries import lookup_country_code
from CTFd.utils.user import is_admin, get_current_team
from CTFd.utils.crypto import verify_password, hash_password


class TeamSchema(ma.ModelSchema):
    class Meta:
        model = Teams
        include_fk = True
        dump_only = ('id', 'oauth_id', 'created', 'members')
        load_only = ('password',)

    name = field_for(
        Teams,
        'name',
        required=True,
        validate=[
            validate.Length(min=1, max=128, error='Team names must not be empty')
        ]
    )
    email = field_for(
        Teams,
        'email',
        validate=validate.Email('Emails must be a properly formatted email address')
    )
    website = field_for(
        Teams,
        'website',
        validate=validate.URL(
            error='Websites must be a proper URL starting with http or https',
            schemes={'http', 'https'}
        )
    )
    country = field_for(
        Teams,
        'country',
        validate=[
            validate_country_code
        ]
    )

    @pre_load
    def validate_name(self, data):
        name = data.get('name')
        if name is None:
            return

        existing_team = Teams.query.filter_by(name=name).first()
        # Admins should be able to patch anyone but they cannot cause a collision.
        if is_admin():
            team_id = int(data.get('id', 0))
            if team_id:
                if existing_team and existing_team.id != team_id:
                    raise ValidationError('Team name has already been taken', field_names=['name'])
            else:
                # If there's no Team ID it means that the admin is creating a team with no ID.
                if existing_team:
                    raise ValidationError('Team name has already been taken', field_names=['name'])
        else:
            current_team = get_current_team()
            # We need to allow teams to edit themselves and allow the "conflict"
            if data['name'] == current_team.name:
                return data
            else:
                name_changes = get_config('name_changes', default=True)
                if bool(name_changes) is False:
                    raise ValidationError('Name changes are disabled', field_names=['name'])

                if existing_team:
                    raise ValidationError('Team name has already been taken', field_names=['name'])

    @pre_load
    def validate_email(self, data):
        email = data.get('email')
        if email is None:
            return

        existing_team = Teams.query.filter_by(email=email).first()
        if is_admin():
            team_id = data.get('id')
            if team_id:
                if existing_team and existing_team.id != team_id:
                    raise ValidationError('Email address has already been used', field_names=['email'])
            else:
                if existing_team:
                    raise ValidationError('Email address has already been used', field_names=['email'])
        else:
            current_team = get_current_team()
            if email == current_team.email:
                return data
            else:
                if existing_team:
                    raise ValidationError('Email address has already been used', field_names=['email'])

    @pre_load
    def validate_password_confirmation(self, data):
        password = data.get('password')
        confirm = data.get('confirm')
        target_team = get_current_team()

        if is_admin():
            pass
        else:
            if password and (confirm is None):
                raise ValidationError('Please confirm your current password', field_names=['confirm'])

            if password and confirm:
                test = verify_password(plaintext=confirm, ciphertext=target_team.password)
                if test is True:
                    return data
                else:
                    raise ValidationError('Your previous password is incorrect', field_names=['confirm'])

    views = {
        'user': [
            'website',
            'name',
            'country',
            'affiliation',
            'bracket',
            'members',
            'id',
            'oauth_id',
        ],
        'self': [
            'website',
            'name',
            'email',
            'country',
            'affiliation',
            'bracket',
            'members',
            'id',
            'oauth_id',
            'password'
        ],
        'admin': [
            'website',
            'name',
            'created',
            'country',
            'banned',
            'email',
            'affiliation',
            'secret',
            'bracket',
            'members',
            'hidden',
            'id',
            'oauth_id',
            'password'
        ]
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if type(view) == str:
                kwargs['only'] = self.views[view]
            elif type(view) == list:
                kwargs['only'] = view

        super(TeamSchema, self).__init__(*args, **kwargs)
