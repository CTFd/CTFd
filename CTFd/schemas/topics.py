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
                # TODO: CTFd 4.0 Passing a list of fields to TopicSchema as the view will be removed
                print(
                    "Passing a list of fields to TopicSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
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
                # TODO: CTFd 4.0 Passing a list of fields to ChallengeTopicSchema as the view will be removed
                print(
                    "Passing a list of fields to ChallengeTopicSchema will be removed in CTFd 4.0. Please pass a view name instead."
                )
                kwargs["only"] = view

        super(ChallengeTopicSchema, self).__init__(*args, **kwargs)
