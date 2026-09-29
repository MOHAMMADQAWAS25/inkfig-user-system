class RegistrationError(Exception):
    """Base registration failure."""


class EmailAlreadyRegisteredError(RegistrationError):
    """The supplied email already belongs to an account."""


class RegistrationProviderError(RegistrationError):
    """The authentication provider could not complete registration."""
