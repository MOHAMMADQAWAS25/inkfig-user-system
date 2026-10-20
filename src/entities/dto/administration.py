from uuid import UUID
from pydantic import BaseModel, Field
from src.entities.enums.role import Role


class UserAdministrationResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    role: Role
    is_active: bool


class UserAdministrationSummary(BaseModel):
    total: int = 0
    active: int = 0
    administrators: int = 0


class UserAdministrationPage(BaseModel):
    items: list[UserAdministrationResponse]
    next_cursor: int | None = None
    total: int = 0
    summary: UserAdministrationSummary = Field(default_factory=UserAdministrationSummary)


class ChangeRoleRequest(BaseModel):
    role: Role


class ChangeStatusRequest(BaseModel):
    is_active: bool
