from CTFd.models import Tags, ma
from CTFd.utils import string_types


class TagSchema(ma.ModelSchema):
    class Meta:
        model = Tags
        include_fk = True
        dump_only = ("id",)

    views = {"admin": ["id", "challenge", "value"], "user": ["value"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                # TODO: CTFd 4.0 Passing a list of fields to TagSchema as the view will be removed
                print(
                    "Passing a list of fields to TagSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
                kwargs["only"] = view

        super(TagSchema, self).__init__(*args, **kwargs)
