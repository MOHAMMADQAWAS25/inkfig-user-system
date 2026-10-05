from enum import StrEnum

class AccountStatus(StrEnum):
    ACTIVE = "active"
    SELF_DEACTIVATED = "self_deactivated"
    ADMIN_SUSPENDED = "admin_suspended"
