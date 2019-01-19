from CTFd.models import ma, Files


class FileSchema(ma.ModelSchema):
    class Meta:
        model = Files
        include_fk = True
        dump_only = ('id', 'type', 'location')

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if type(view) == str:
                kwargs['only'] = self.views[view]
            elif type(view) == list:
                kwargs['only'] = view

        super(FileSchema, self).__init__(*args, **kwargs)
