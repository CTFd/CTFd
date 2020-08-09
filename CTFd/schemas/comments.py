from CTFd.models import Comments, ma


class CommentSchema(ma.ModelSchema):
    class Meta:
        model = Comments
        include_fk = True
        dump_only = ("id", "date")
