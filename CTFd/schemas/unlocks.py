from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load
from marshmallow import validate, ValidationError
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Unlocks


class UnlockSchema(ma.ModelSchema):
    class Meta:
        model = Unlocks
        include_fk = True
        dump_only = ('id', 'date')

    views = {
        'admin': [
            'user_id',
            'target',
            'team_id',
            'date',
            'type',
            'id'
        ],
        'user': [
            'target',
            'date',
            'type',
            'id'
        ]
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if type(view) == str:
                kwargs['only'] = self.views[view]
            elif type(view) == list:
                kwargs['only'] = view

        super(UnlockSchema, self).__init__(*args, **kwargs)
