from uuid import UUID
from pydantic import BaseModel
from src.entities.enums.role import Role


class UserAdministrationResponse(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    role: Role
    is_active: bool


class ChangeRoleRequest(BaseModel):
    role: Role


class ChangeStatusRequest(BaseModel):
    is_active: bool
