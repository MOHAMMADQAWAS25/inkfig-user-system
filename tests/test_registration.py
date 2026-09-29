from datetime import date, datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.app.services.registration_service import RegistrationService
from src.entities.dto.registration import (
    RegisteredUser,
    RegisterUserRequest,
    UserProfileCreate,
)
from src.entities.enums.gender import Gender


def registration_request(**overrides: object) -> RegisterUserRequest:
    values: dict[str, object] = {
        "email": "12345678@students.hebron.edu",
        "full_name": "Student Name",
        "phone_number": "0599123456",
        "gender": "female",
        "date_of_birth": "2002-05-17",
        "password": "correct-password",
        "password_confirmation": "correct-password",
    }
    values.update(overrides)
    return RegisterUserRequest.model_validate(values)


@pytest.mark.parametrize(
    "email",
    ["12345678@students.hebron.edu", "teacher.name@hebron.edu"],
)
def test_registration_accepts_hebron_email_formats(email: str) -> None:
    assert registration_request(email=email).email == email


@pytest.mark.parametrize(
    "email",
    ["1234567@students.hebron.edu", "123456789@students.hebron.edu", "user@gmail.com"],
)
def test_registration_rejects_non_hebron_email_formats(email: str) -> None:
    with pytest.raises(ValidationError):
        registration_request(email=email)


def test_registration_requires_matching_passwords() -> None:
    with pytest.raises(ValidationError):
        registration_request(password_confirmation="different-password")


@pytest.mark.parametrize(
    "phone_number",
    ["059912345", "05991234567", "+970599123456", "05991abc56"],
)
def test_registration_rejects_phone_numbers_without_exactly_ten_digits(
    phone_number: str,
) -> None:
    with pytest.raises(ValidationError):
        registration_request(phone_number=phone_number)


@pytest.mark.parametrize(
    "field",
    [
        "email",
        "full_name",
        "phone_number",
        "gender",
        "date_of_birth",
        "password",
        "password_confirmation",
    ],
)
def test_registration_requires_every_field(field: str) -> None:
    values = registration_request().model_dump()
    values.pop(field)
    with pytest.raises(ValidationError):
        RegisterUserRequest.model_validate(values)


class FakeAuthGateway:
    def __init__(self) -> None:
        self.user_id = uuid4()
        self.deleted_user_id: UUID | None = None

    async def create_user(self, email: str, password: str) -> UUID:
        return self.user_id

    async def delete_user(self, user_id: UUID) -> None:
        self.deleted_user_id = user_id


class FakeProfileRepository:
    async def create(self, profile: UserProfileCreate) -> RegisteredUser:
        return RegisteredUser(
            **profile.model_dump(),
            is_active=True,
            created_at=datetime.now(timezone.utc),
        )


class FailingProfileRepository:
    async def create(self, profile: UserProfileCreate) -> RegisteredUser:
        raise RuntimeError("database failure")


@pytest.mark.asyncio
async def test_registration_creates_auth_user_and_profile() -> None:
    auth_gateway = FakeAuthGateway()
    service = RegistrationService(auth_gateway, FakeProfileRepository())

    result = await service.register(registration_request())

    assert result.user.user_id == auth_gateway.user_id
    assert result.user.gender is Gender.FEMALE
    assert result.user.date_of_birth == date(2002, 5, 17)


@pytest.mark.asyncio
async def test_registration_removes_auth_user_when_profile_creation_fails() -> None:
    auth_gateway = FakeAuthGateway()
    service = RegistrationService(auth_gateway, FailingProfileRepository())

    with pytest.raises(RuntimeError, match="database failure"):
        await service.register(registration_request())

    assert auth_gateway.deleted_user_id == auth_gateway.user_id
