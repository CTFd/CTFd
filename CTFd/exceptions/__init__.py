class UserNotFoundException(Exception):
    pass


class UserTokenExpiredException(Exception):
    pass


class TeamTokenExpiredException(Exception):
    pass


class TeamTokenInvalidException(Exception):
    pass


class InvalidLanguageException(Exception):
    pass
