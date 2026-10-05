from datetime import date

from pydantic import BaseModel, Field, ValidationInfo, field_validator

from src.entities.dto.registration import RegisterUserRequest
from src.entities.enums.gender import Gender


class ProfileSettingsResponse(BaseModel):
    email: str
    full_name: str
    phone_number: str
    gender: Gender
    date_of_birth: date
    is_active: bool


class UpdateProfileSettingsRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    phone_number: str = Field(min_length=10, max_length=10)
    gender: Gender
    date_of_birth: date

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        return RegisterUserRequest.validate_full_name(value)

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, value: str) -> str:
        return RegisterUserRequest.validate_phone_number(value)

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date) -> date:
        return RegisterUserRequest.validate_date_of_birth(value)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    password: str = Field(min_length=8, max_length=128)
    password_confirmation: str = Field(min_length=8, max_length=128)

    @field_validator("password_confirmation")
    @classmethod
    def password_matches(cls, value: str, info: ValidationInfo) -> str:
        if value != info.data.get("password"):
            raise ValueError("Password and password confirmation must match.")
        return value


class AccountStatusRequest(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
