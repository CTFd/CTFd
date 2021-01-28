from marshmallow import ValidationError, pre_load

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

    @pre_load
    def validate_content(self, data):
        content = data.get("content")
        print(repr(content[0:200]))
        print(len(content))
        if len(content) >= 65536:
            raise ValidationError(
                "Page could not be saved. Your content is too long.", field_names=["content"]
            )

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(PageSchema, self).__init__(*args, **kwargs)
