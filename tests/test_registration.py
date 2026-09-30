from datetime import date, datetime, timezone
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from src.app.services.registration_service import RegistrationService
from src.entities.dto.registration import (
    EmailVerificationCreate,
    PendingEmailVerification,
    RegisteredUser,
    RegisterUserRequest,
    UserProfileCreate,
)
from src.entities.enums.gender import Gender
from src.entities.exceptions.registration import (
    VerificationCodeExpiredError,
    VerificationCodeInvalidError,
)


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


class FakePasswordHasher:
    def hash(self, password: str) -> str:
        return f"hashed:{password}"

    def verify(self, password: str, encoded: str) -> bool:
        return encoded == self.hash(password)


class FakeProfileRepository:
    def __init__(self) -> None:
        self.challenge: PendingEmailVerification | None = None
        self.failed_attempts = 0
        self.activated = False

    async def create_pending(
        self, profile: UserProfileCreate, verification: EmailVerificationCreate
    ) -> RegisteredUser:
        self.challenge = PendingEmailVerification(
            verification_id=uuid4(),
            user_id=profile.user_id,
            email=profile.email,
            full_name=profile.full_name,
            code_hash=verification.code_hash,
            expires_at=verification.expires_at,
            attempts=0,
            max_attempts=verification.max_attempts,
            sent_at=datetime.now(timezone.utc),
        )
        return RegisteredUser(
            **profile.model_dump(),
            is_active=False,
            created_at=datetime.now(timezone.utc),
        )

    async def get_pending_verification(self, email: str) -> PendingEmailVerification | None:
        return self.challenge

    async def record_failed_attempt(self, verification_id: UUID) -> None:
        self.failed_attempts += 1

    async def activate_verified_user(
        self, verification_id: UUID, user_id: UUID, verified_at: datetime
    ) -> None:
        self.activated = True

    async def replace_verification(
        self, previous_id: UUID, verification: EmailVerificationCreate
    ) -> None:
        if self.challenge:
            self.challenge = self.challenge.model_copy(
                update={
                    "verification_id": uuid4(),
                    "code_hash": verification.code_hash,
                    "expires_at": verification.expires_at,
                    "attempts": 0,
                    "sent_at": datetime.now(timezone.utc),
                }
            )


class FailingProfileRepository:
    async def create_pending(
        self, profile: UserProfileCreate, verification: EmailVerificationCreate
    ) -> RegisteredUser:
        raise RuntimeError("database failure")

    async def get_pending_verification(self, email: str) -> PendingEmailVerification | None:
        return None

    async def record_failed_attempt(self, verification_id: UUID) -> None:
        return None

    async def activate_verified_user(
        self, verification_id: UUID, user_id: UUID, verified_at: datetime
    ) -> None:
        return None

    async def replace_verification(
        self, previous_id: UUID, verification: EmailVerificationCreate
    ) -> None:
        return None


class FakeEmailGateway:
    def __init__(self) -> None:
        self.code = ""

    async def send_verification_code(
        self, email: str, full_name: str, code: str, expires_minutes: int
    ) -> None:
        self.code = code


@pytest.mark.asyncio
async def test_registration_creates_auth_user_and_profile() -> None:
    repository = FakeProfileRepository()
    email_gateway = FakeEmailGateway()
    service = RegistrationService(repository, email_gateway, FakePasswordHasher(), "test-secret")

    result = await service.register(registration_request())

    assert result.email == "12345678@students.hebron.edu"
    assert result.verification_required is True
    assert repository.challenge is not None
    assert repository.challenge.code_hash != email_gateway.code
    assert len(email_gateway.code) == 6


@pytest.mark.asyncio
async def test_registration_propagates_database_failure() -> None:
    service = RegistrationService(
        FailingProfileRepository(), FakeEmailGateway(), FakePasswordHasher(), "test-secret"
    )

    with pytest.raises(RuntimeError, match="database failure"):
        await service.register(registration_request())

@pytest.mark.asyncio
async def test_registration_resumes_existing_pending_verification() -> None:
    repository = FakeProfileRepository()
    email_gateway = FakeEmailGateway()
    initial_service = RegistrationService(
        repository, email_gateway, FakePasswordHasher(), "test-secret"
    )
    await initial_service.register(registration_request())
    assert repository.challenge is not None
    original_verification_id = repository.challenge.verification_id

    repository.challenge = repository.challenge.model_copy(
        update={"sent_at": datetime(2020, 1, 1, tzinfo=timezone.utc)}
    )
    service = RegistrationService(
        repository,
        email_gateway,
        FakePasswordHasher(),
        "test-secret",
    )

    result = await service.register(registration_request())

    assert result.verification_required is True
    assert repository.challenge.verification_id != original_verification_id
    assert repository.challenge.code_hash != email_gateway.code


@pytest.mark.asyncio
async def test_correct_code_confirms_and_activates_account() -> None:
    repository = FakeProfileRepository()
    email_gateway = FakeEmailGateway()
    service = RegistrationService(repository, email_gateway, FakePasswordHasher(), "test-secret")
    await service.register(registration_request())

    result = await service.verify_email(registration_request().email, email_gateway.code)

    assert result.verified is True
    assert repository.activated is True


@pytest.mark.asyncio
async def test_incorrect_code_records_failed_attempt() -> None:
    repository = FakeProfileRepository()
    service = RegistrationService(repository, FakeEmailGateway(), FakePasswordHasher(), "test-secret")
    await service.register(registration_request())

    with pytest.raises(VerificationCodeInvalidError):
        await service.verify_email(registration_request().email, "999999")

    assert repository.failed_attempts == 1


@pytest.mark.asyncio
async def test_expired_code_is_rejected() -> None:
    repository = FakeProfileRepository()
    service = RegistrationService(repository, FakeEmailGateway(), FakePasswordHasher(), "test-secret")
    await service.register(registration_request())
    assert repository.challenge is not None
    repository.challenge = repository.challenge.model_copy(
        update={"expires_at": datetime(2020, 1, 1, tzinfo=timezone.utc)}
    )

    with pytest.raises(VerificationCodeExpiredError):
        await service.verify_email(registration_request().email, "000000")
