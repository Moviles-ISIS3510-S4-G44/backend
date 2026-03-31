class InternalAuthError(Exception):
    pass


class DuplicateUserError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AuthSessionNotFoundError(Exception):
    pass


class InactiveAuthSessionError(Exception):
    pass


class ExpiredAuthSessionError(Exception):
    pass


class InvalidRefreshTokenError(Exception):
    pass
