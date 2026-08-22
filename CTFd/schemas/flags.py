from CTFd.models import Flags, ma
from CTFd.utils import string_types


class FlagSchema(ma.ModelSchema):
    class Meta:
        model = Flags
        include_fk = True
        dump_only = ("id",)

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                # TODO: CTFd 4.0 Passing a list of fields to FlagSchema as the view will be removed
                print(
                    "Passing a list of fields to FlagSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
                kwargs["only"] = view

        super(FlagSchema, self).__init__(*args, **kwargs)
