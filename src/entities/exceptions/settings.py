class SettingsError(Exception):
    pass


class ProfileNotFoundError(SettingsError):
    pass


class PhoneNumberAlreadyExistsError(SettingsError):
    pass


class CurrentPasswordInvalidError(SettingsError):
    pass
