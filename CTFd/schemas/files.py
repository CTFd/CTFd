from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load
from marshmallow import validate, ValidationError
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Files, ChallengeFiles, PageFiles
from CTFd.utils import string_types


class FileSchema(ma.ModelSchema):
    class Meta:
        model = Files
        include_fk = True
        dump_only = ('id', 'type', 'location')

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs['only'] = self.views[view]
            elif isinstance(view, list):
                kwargs['only'] = view

        super(FileSchema, self).__init__(*args, **kwargs)
