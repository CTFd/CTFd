from CTFd.models import AudienceMembers, Audiences, ma


class AudienceSchema(ma.ModelSchema):
    class Meta:
        model = Audiences
        include_fk = True
        dump_only = ("id",)


class AudienceMemberSchema(ma.ModelSchema):
    class Meta:
        model = AudienceMembers
        include_fk = True
        dump_only = ("id",)
