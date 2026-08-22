from CTFd.models import Files, ma
from CTFd.utils import string_types


class FileSchema(ma.ModelSchema):
    class Meta:
        model = Files
        include_fk = True
        dump_only = ("id", "type", "location")

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                # TODO: CTFd 4.0 Passing a list of fields to FileSchema as the view will be removed
                print(
                    "Passing a list of fields to FileSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
                kwargs["only"] = view

        super(FileSchema, self).__init__(*args, **kwargs)
