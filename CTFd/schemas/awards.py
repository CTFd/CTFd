from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load
from marshmallow import validate, ValidationError
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Awards


class AwardSchema(ma.ModelSchema):
    class Meta:
        model = Awards
        include_fk = True
        dump_only = ('id', 'date')

    views = {
        'admin': [
            'category',
            'user_id',
            'name',
            'description',
            'value',
            'team_id',
            'user',
            'team',
            'date',
            'requirements',
            'id',
            'icon'
        ],
        'user': [
            'category',
            'user_id',
            'name',
            'description',
            'value',
            'team_id',
            'user',
            'team',
            'date',
            'id',
            'icon'
        ]
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if type(view) == str:
                kwargs['only'] = self.views[view]
            elif type(view) == list:
                kwargs['only'] = view

        super(AwardSchema, self).__init__(*args, **kwargs)
