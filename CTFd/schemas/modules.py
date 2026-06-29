from CTFd.models import ModuleAudienceAccess, Modules, ma


class ModuleSchema(ma.ModelSchema):
    class Meta:
        model = Modules
        include_fk = True
        dump_only = ("id",)


class ModuleAudienceAccessSchema(ma.ModelSchema):
    class Meta:
        model = ModuleAudienceAccess
        include_fk = True
        dump_only = ("id",)
