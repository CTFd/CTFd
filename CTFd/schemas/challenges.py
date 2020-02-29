from CTFd.models import Challenges, ma


class ChallengeSchema(ma.ModelSchema):
    class Meta:
        model = Challenges
        include_fk = True
        dump_only = ("id",)
