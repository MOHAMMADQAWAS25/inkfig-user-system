from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from src.entities.dto.registration import RegisterUserRequest


class LoginRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return RegisterUserRequest.validate_hebron_email(value)


class AuthenticatedUser(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    password_hash: str
    is_active: bool
    email_verified_at: datetime | None
    token_version: int


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID
    email: str
    full_name: str
    permissions: list[str] = []


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=32, max_length=512)


class LogoutRequest(RefreshTokenRequest):
    pass
