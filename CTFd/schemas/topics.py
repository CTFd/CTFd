from CTFd.models import ChallengeTopics, Topics, ma
from CTFd.utils import string_types


class TopicSchema(ma.ModelSchema):
    class Meta:
        model = Topics
        include_fk = True
        dump_only = ("id",)

    views = {"admin": ["id", "value"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(TopicSchema, self).__init__(*args, **kwargs)


class ChallengeTopicSchema(ma.ModelSchema):
    class Meta:
        model = ChallengeTopics
        include_fk = True
        dump_only = ("id",)

    views = {"admin": ["id", "challenge_id", "topic_id"]}

    def __init__(self, view=None, *args, **kwargs):
        if view:
            if isinstance(view, string_types):
                kwargs["only"] = self.views[view]
            elif isinstance(view, list):
                kwargs["only"] = view

        super(ChallengeTopicSchema, self).__init__(*args, **kwargs)
