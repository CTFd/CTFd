from sqlalchemy.sql.expression import union_all
from marshmallow import fields, post_load
from marshmallow import validate, ValidationError, pre_load
from marshmallow_sqlalchemy import field_for
from CTFd.models import ma, Pages


class PageSchema(ma.ModelSchema):
    class Meta:
        model = Pages
        include_fk = True
        dump_only = ('id', )

    @pre_load
    def validate_route(self, data):
        route = data.get('route')
        if route and route.startswith('/'):
            data['route'] = route.strip('/')

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if type(view) == str:
                kwargs['only'] = self.views[view]
            elif type(view) == list:
                kwargs['only'] = view

        super(PageSchema, self).__init__(*args, **kwargs)
