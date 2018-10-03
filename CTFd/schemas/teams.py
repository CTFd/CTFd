from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load
from marshmallow import validate, ValidationError
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Teams
from CTFd.utils.validators import unique_team_name


class TeamSchema(ma.ModelSchema):
    class Meta:
        model = Teams
        dump_only = ('id', 'oauth_id', 'created', 'members')
        load_only = ('password',)

    name = field_for(
        Teams,
        'name',
        required=True,
        validate=[
            unique_team_name,
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
    # TODO: Countries should be validated against the countries list
    # country = field_for(
    #     Teams,
    #     'country'
    # )

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