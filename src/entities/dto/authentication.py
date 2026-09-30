from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ValidationInfo, field_validator

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


class PasswordResetRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return RegisterUserRequest.validate_hebron_email(value)


class PasswordResetRequestResponse(BaseModel):
    message: str = "If the account exists, a reset code has been sent."
    expires_in_seconds: int = 600


class PasswordResetVerifyRequest(PasswordResetRequest):
    code: str = Field(pattern=r"^[0-9]{6}$")


class PasswordResetVerifyResponse(BaseModel):
    reset_token: str
    expires_in_seconds: int


class PasswordResetConfirmRequest(PasswordResetRequest):
    reset_token: str = Field(min_length=32, max_length=512)
    password: str = Field(min_length=8, max_length=128)
    password_confirmation: str = Field(min_length=8, max_length=128)

    @field_validator("password_confirmation")
    @classmethod
    def password_matches(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data.get("password"):
            raise ValueError("Password and password confirmation must match.")
        return value


class PasswordResetChallenge(BaseModel):
    challenge_id: UUID
    user_id: UUID
    email: str
    code_hash: str
    expires_at: datetime
    attempts: int
    max_attempts: int
