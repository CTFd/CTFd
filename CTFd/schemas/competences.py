from CTFd.models import Competences, ma
from CTFd.utils import string_types


class CompetenceSchema(ma.ModelSchema):
    class Meta:
        model = Competences
        include_fk = True
        dump_only = ("id",)

    views = {"user": ["name"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view
        super(CompetenceSchema, self).__init__(*args, **kwargs)
