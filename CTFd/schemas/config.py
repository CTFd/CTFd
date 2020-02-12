from CTFd.models import Configs, ma
from CTFd.utils import string_types


class ConfigSchema(ma.ModelSchema):
    class Meta:
        model = Configs
        include_fk = True
        dump_only = ("id",)

    views = {"admin": ["id", "key", "value"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(ConfigSchema, self).__init__(*args, **kwargs)
