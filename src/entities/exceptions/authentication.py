class AuthenticationError(Exception):
    """Base authentication failure."""


class InvalidCredentialsError(AuthenticationError):
    """Email or password is invalid."""


class AccountInactiveError(AuthenticationError):
    """The account is not active and verified."""

class AccountAdminSuspendedError(AuthenticationError):
    """The account was suspended by an administrator."""


class InvalidRefreshTokenError(AuthenticationError):
    """The refresh token is invalid, expired, or revoked."""


class PasswordResetCodeInvalidError(AuthenticationError):
    pass


class PasswordResetCodeExpiredError(AuthenticationError):
    pass


class PasswordResetAttemptsExceededError(AuthenticationError):
    pass


class PasswordResetTokenInvalidError(AuthenticationError):
    pass
