class RegistrationError(Exception):
    """Base registration failure."""


class EmailAlreadyRegisteredError(RegistrationError):
    """The supplied email already belongs to an account."""


class RegistrationProviderError(RegistrationError):
    """The authentication provider could not complete registration."""


class EmailDeliveryError(RegistrationError):
    """The verification email could not be delivered."""


class VerificationCodeInvalidError(RegistrationError):
    """The supplied verification code is invalid."""


class VerificationCodeExpiredError(RegistrationError):
    """The verification code has expired."""


class VerificationAttemptsExceededError(RegistrationError):
    """The verification challenge has no attempts remaining."""


class VerificationResendTooSoonError(RegistrationError):
    """A replacement code was requested before the cooldown elapsed."""


class VerificationNotFoundError(RegistrationError):
    """No pending verification challenge exists for the email."""
