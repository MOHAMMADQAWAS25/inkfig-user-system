from enum import StrEnum


class Role(StrEnum):
    VIEWER = "viewer"
    USER = "user"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    SYSTEM_ADMINISTRATOR = "system_administrator"


ROLE_RANK = {
    Role.VIEWER: 10,
    Role.USER: 20,
    Role.SUPERVISOR: 40,
    Role.ADMIN: 80,
    Role.SYSTEM_ADMINISTRATOR: 100,
}
