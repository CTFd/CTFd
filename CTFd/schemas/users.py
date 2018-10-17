from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load
from marshmallow import validate, ValidationError, pre_load
from marshmallow.decorators import validates_schema
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Users
from CTFd.utils.validators import unique_email, unique_team_name, validate_country_code
from CTFd.utils.user import is_admin, get_current_user
from CTFd.utils.countries import lookup_country_code


class UserSchema(ma.ModelSchema):
    class Meta:
        model = Users
        dump_only = ('id', 'oauth_id', 'created')
        load_only = ('password',)

    name = field_for(
        Users,
        'name',
        required=True,
        validate=[
            unique_team_name,
            validate.Length(min=1, max=128, error='Team names must not be empty')
        ]
    )
    email = field_for(
        Users,
        'email',
        validate=[
            validate.Email('Emails must be a properly formatted email address'),
            validate.Length(min=1, max=128, error='Emails must not be empty'),
        ]
    )
    website = field_for(
        Users,
        'website',
        validate=validate.URL(
            error='Websites must be a proper URL starting with http or https',
            schemes={'http', 'https'}
        )
    )
    country = field_for(
        Users,
        'country',
        validate=[
            validate_country_code
        ]
    )
    # password = field_for(
    #
    # )

    @pre_load
    def validate_email(self, data):
        email = data.get('email')
        if email is None:
            return
        obj = Users.query.filter_by(email=email).first()
        if obj:
            if is_admin():
                target_user = Users.query.filter_by(id=data['id']).first()
                if target_user and obj.id != target_user.id:
                    raise ValidationError('Email address has already been used')
            else:
                if obj.id != get_current_user().id:
                    raise ValidationError('Email address has already been used')
                # data['verified'] = False
                # return data
    views = {
        'user': [
            'website',
            'name',
            'country',
            'affiliation',
            'bracket',
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

        super(UserSchema, self).__init__(*args, **kwargs)