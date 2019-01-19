from CTFd.models import ma, Hints


class HintSchema(ma.ModelSchema):
    class Meta:
        model = Hints
        include_fk = True
        dump_only = ('id', 'type')

    views = {
        'locked': [
            'id',
            'type',
            'challenge',
            'cost'
        ],
        'unlocked': [
            'id',
            'type',
            'challenge',
            'content',
            'cost'
        ],
        'admin': [
            'id',
            'type',
            'challenge',
            'content',
            'cost',
            'requirements'
        ]
    }

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if type(view) == str:
                kwargs['only'] = self.views[view]
            elif type(view) == list:
                kwargs['only'] = view

        super(HintSchema, self).__init__(*args, **kwargs)
