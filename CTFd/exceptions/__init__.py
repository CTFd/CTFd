class UserNotFoundException(Exception):
    pass


class UserTokenExpiredException(Exception):
    pass


class TeamTokenExpiredException(Exception):
    pass


class TeamTokenInvalidException(Exception):
    pass


class PluginDependencyException(Exception):
    def __init__(self, dependencies: list, *args):
        super().__init__(*args)
        if (
            isinstance(self.dependencies, list) and
            all((isinstance(d, str) for d in dependencies))
        ):
            self.dependencies = dependencies
        else:
            self.dependencies = []
