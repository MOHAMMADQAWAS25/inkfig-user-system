import re
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator

from src.entities.enums.gender import Gender
from src.entities.dto.profile_avatar import AvatarUploadResponse


STUDENT_EMAIL_PATTERN = re.compile(r"^\d{8}@students\.hebron\.edu$")
STAFF_EMAIL_PATTERN = re.compile(
    r"^[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@hebron\.edu$"
)
PHONE_PATTERN = re.compile(r"^[0-9]{10}$")


class RegisterUserRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    full_name: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(min_length=7, max_length=24)
    gender: Gender
    date_of_birth: date
    password: str = Field(min_length=8, max_length=128)
    password_confirmation: str = Field(min_length=8, max_length=128)
    avatar_file_name: str | None = Field(default=None, max_length=255)
    avatar_mime_type: str | None = Field(default=None, max_length=100)
    avatar_file_size: int | None = Field(default=None, gt=0, le=2 * 1024 * 1024)

    @field_validator("email")
    @classmethod
    def validate_hebron_email(cls, value: str) -> str:
        normalized = value.strip().lower()
        if not (
            STUDENT_EMAIL_PATTERN.fullmatch(normalized)
            or STAFF_EMAIL_PATTERN.fullmatch(normalized)
        ):
            raise ValueError(
                "Email must be 8 digits followed by @students.hebron.edu "
                "or a valid @hebron.edu address."
            )
        return normalized

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        normalized = value.strip().replace(" ", "").replace("-", "")
        if not PHONE_PATTERN.fullmatch(normalized):
            raise ValueError("Phone number must contain exactly 10 digits.")
        return normalized

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        normalized = " ".join(value.split())
        if len(normalized) < 2:
            raise ValueError("Full name is required.")
        return normalized

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Date of birth must be in the past.")
        return value

    @model_validator(mode="after")
    def validate_password_confirmation(self) -> "RegisterUserRequest":
        if self.password != self.password_confirmation:
            raise ValueError("Password and password confirmation must match.")
        avatar_values = (self.avatar_file_name, self.avatar_mime_type, self.avatar_file_size)
        if any(value is not None for value in avatar_values) and not all(value is not None for value in avatar_values):
            raise ValueError("Avatar file metadata must be complete.")
        return self


class UserProfileCreate(BaseModel):
    user_id: UUID
    password_hash: str
    email: str
    full_name: str
    phone_number: str
    gender: Gender
    date_of_birth: date


class EmailVerificationCreate(BaseModel):
    user_id: UUID
    code_hash: str = Field(min_length=64, max_length=64)
    expires_at: datetime
    max_attempts: int = Field(gt=0)


class PendingEmailVerification(BaseModel):
    verification_id: UUID
    user_id: UUID
    email: str
    full_name: str
    code_hash: str
    expires_at: datetime
    attempts: int
    max_attempts: int
    sent_at: datetime


class RegisteredUser(BaseModel):
    user_id: UUID
    email: str
    full_name: str
    phone_number: str
    gender: Gender
    date_of_birth: date
    is_active: bool
    created_at: datetime


class RegisterUserResponse(BaseModel):
    email: str
    verification_required: bool = True
    expires_in_seconds: int
    resend_after_seconds: int
    hourly_limit_reached: bool = False
    avatar_upload: AvatarUploadResponse | None = None


class VerifyEmailRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)
    code: str = Field(pattern=r"^[0-9]{6}$")
    avatar_object_path: str | None = Field(default=None, max_length=512)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return RegisterUserRequest.validate_hebron_email(value)


class VerifyEmailResponse(BaseModel):
    email: str
    verified: bool = True


class ResendVerificationRequest(BaseModel):
    email: str = Field(min_length=1, max_length=254)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return RegisterUserRequest.validate_hebron_email(value)


class ResendVerificationResponse(BaseModel):
    email: str
    expires_in_seconds: int
    resend_after_seconds: int
    hourly_limit_reached: bool = False
