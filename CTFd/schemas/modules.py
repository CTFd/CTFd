from CTFd.models import Challenges, ModuleAudienceAccess, Modules, ma


class ModuleSchema(ma.ModelSchema):
    class Meta:
        model = Modules
        include_fk = True
        dump_only = ("id",)


class ModuleChallengeSchema(ma.ModelSchema):
    class Meta:
        model = Challenges
        fields = ("id", "name", "category", "module_id")
        dump_only = ("id",)


class ModuleAudienceAccessSchema(ma.ModelSchema):
    class Meta:
        model = ModuleAudienceAccess
        include_fk = True
        dump_only = ("id",)
        exclude = ("module", "audience")
