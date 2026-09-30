class AuthenticationError(Exception):
    """Base authentication failure."""


class InvalidCredentialsError(AuthenticationError):
    """Email or password is invalid."""


class AccountInactiveError(AuthenticationError):
    """The account is not active and verified."""


class InvalidRefreshTokenError(AuthenticationError):
    """The refresh token is invalid, expired, or revoked."""
