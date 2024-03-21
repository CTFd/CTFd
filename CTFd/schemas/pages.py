from marshmallow import pre_load, validate
from marshmallow_sqlalchemy import field_for

from CTFd.models import Pages, ma
from CTFd.utils import string_types


class PageSchema(ma.ModelSchema):
    class Meta:
        model = Pages
        include_fk = True
        dump_only = ("id",)

    title = field_for(
        Pages,
        "title",
        validate=[
            validate.Length(
                min=0,
                max=80,
                error="Page could not be saved. Your title is too long.",
            )
        ],
    )

    route = field_for(
        Pages,
        "route",
        allow_none=True,
        validate=[
            validate.Length(
                min=0,
                max=128,
                error="Page could not be saved. Your route is too long.",
            )
        ],
    )

    content = field_for(
        Pages,
        "content",
        allow_none=True,
        validate=[
            validate.Length(
                min=0,
                max=65535,
                error="Page could not be saved. Your content is too long.",
            )
        ],
    )

    link_target = field_for(
        Pages,
        "link_target",
        allow_none=True,
        validate=[
            validate.OneOf(
                choices=[None, "_self", "_blank"],
                error="Invalid link target",
            )
        ],
    )

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
