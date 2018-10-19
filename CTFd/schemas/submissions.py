from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load
from marshmallow import validate, ValidationError
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Submissions


class SubmissionSchema(ma.ModelSchema):
    class Meta:
        model = Submissions
        dump_only = ('id', )
        # load_only = ('password',)

    views = {
        'admin': [
            'provided',
            'ip',
            'challenge',
            'user',
            'team',
            'date',
            'type',
            'id'
        ],
        'user': [
            'ip',
            'challenge',
            'user',
            'team',
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

        super(SubmissionSchema, self).__init__(*args, **kwargs)
