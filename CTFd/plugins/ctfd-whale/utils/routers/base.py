import typing

from ...models import WhaleContainer


class BaseRouter:
    name = None

    def __init__(self):
        pass

    def access(self, container: WhaleContainer):
        pass

    def register(self, container: WhaleContainer):
        pass

    def unregister(self, container: WhaleContainer):
        pass

    def reload(self):
        pass

    def check_availability(self) -> typing.Tuple[bool, str]:
        pass
