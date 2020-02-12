from marshmallow import pre_load

from CTFd.models import Pages, ma
from CTFd.utils import string_types


class PageSchema(ma.ModelSchema):
    class Meta:
        model = Pages
        include_fk = True
        dump_only = ("id",)

    @pre_load
    def validate_route(self, data):
        route = data.get("route")
        if route and route.startswith("/"):
            data["route"] = route.strip("/")

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(PageSchema, self).__init__(*args, **kwargs)
