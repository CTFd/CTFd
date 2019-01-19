from CTFd.models import ma, Flags


class FlagSchema(ma.ModelSchema):
    class Meta:
        model = Flags
        include_fk = True
        dump_only = ('id',)

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if type(view) == str:
                kwargs['only'] = self.views[view]
            elif type(view) == list:
                kwargs['only'] = view

        super(FlagSchema, self).__init__(*args, **kwargs)
