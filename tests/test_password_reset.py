from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import pytest

from src.app.services.password_reset_service import PasswordResetService
from src.entities.dto.authentication import AuthenticatedUser, PasswordResetChallenge
from src.entities.dto.email_code_rate_limit import EmailCodeRateDecision
from src.entities.exceptions.authentication import (
    PasswordResetAttemptsExceededError,
    PasswordResetCodeExpiredError,
    PasswordResetCodeInvalidError,
    PasswordResetTokenInvalidError,
)
from src.infrastructure.security.passwords import Pbkdf2PasswordHasher

SECRET = "a-long-test-jwt-secret-with-32-bytes-minimum"


class FakeAuthenticationRepository:
    def __init__(self, user: AuthenticatedUser | None) -> None:
        self.user = user

    async def find_user_by_email(self, email: str) -> AuthenticatedUser | None:
        return self.user if self.user and self.user.email == email else None

    async def reactivate_self_deactivated(self, user_id: UUID) -> AuthenticatedUser:
        raise NotImplementedError

    async def store_refresh_token(self, *args: object) -> None:
        raise NotImplementedError

    async def consume_refresh_token(self, *args: object) -> AuthenticatedUser | None:
        raise NotImplementedError

    async def revoke_refresh_token(self, *args: object) -> None:
        raise NotImplementedError


class FakeResetRepository:
    def __init__(self, email: str) -> None:
        self.email = email
        self.challenge: PasswordResetChallenge | None = None
        self.reset_token_hash: str | None = None
        self.reset_token_expires_at: datetime | None = None
        self.new_password_hash: str | None = None
        self.reset_succeeds = True

    async def create_challenge(
        self, user_id: UUID, code_hash: str, expires_at: datetime, max_attempts: int
    ) -> None:
        self.challenge = PasswordResetChallenge(
            challenge_id=uuid4(),
            user_id=user_id,
            email=self.email,
            code_hash=code_hash,
            expires_at=expires_at,
            attempts=0,
            max_attempts=max_attempts,
        )

    async def get_pending(self, email: str) -> PasswordResetChallenge | None:
        return self.challenge if email == self.email else None

    async def record_failed_attempt(self, challenge_id: UUID) -> None:
        assert self.challenge and self.challenge.challenge_id == challenge_id
        self.challenge.attempts += 1

    async def verify_challenge(
        self,
        challenge_id: UUID,
        token_hash: str,
        token_expires_at: datetime,
        verified_at: datetime,
    ) -> None:
        assert self.challenge and self.challenge.challenge_id == challenge_id
        self.reset_token_hash = token_hash
        self.reset_token_expires_at = token_expires_at

    async def reset_password(
        self, email: str, token_hash: str, password_hash: str, now: datetime
    ) -> bool:
        if not self.reset_succeeds or token_hash != self.reset_token_hash:
            return False
        self.new_password_hash = password_hash
        return True


class FakeEmailGateway:
    def __init__(self) -> None:
        self.messages: list[tuple[str, str, str, int]] = []

    async def send_password_reset_code(
        self, email: str, full_name: str, code: str, expires_minutes: int
    ) -> None:
        self.messages.append((email, full_name, code, expires_minutes))


class FakeRateLimitRepository:
    def __init__(self, decision: EmailCodeRateDecision) -> None:
        self.decision = decision
        self.identifier_hash = ""

    async def reserve_send(
        self,
        scope: str,
        identifier_hash: str,
        now: datetime,
        cooldown_seconds: int,
        max_sends: int,
        block_seconds: int,
    ) -> EmailCodeRateDecision:
        assert scope == "password-reset"
        self.identifier_hash = identifier_hash
        return self.decision


def make_user() -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=uuid4(),
        email="12345678@students.hebron.edu",
        full_name="Student Name",
        password_hash="old-hash",
        is_active=True,
        email_verified_at=datetime.now(timezone.utc),
        token_version=0,
    )


def make_service(
    *, account_exists: bool = True,
) -> tuple[PasswordResetService, FakeResetRepository, FakeEmailGateway]:
    actual_user = make_user()
    repository = FakeResetRepository(actual_user.email)
    email_gateway = FakeEmailGateway()
    service = PasswordResetService(
        FakeAuthenticationRepository(actual_user if account_exists else None),
        repository,
        email_gateway,
        Pbkdf2PasswordHasher(),
        SECRET,
    )
    return service, repository, email_gateway


@pytest.mark.asyncio
async def test_request_stores_a_hash_and_sends_six_digit_code() -> None:
    service, repository, email_gateway = make_service()
    response = await service.request("12345678@students.hebron.edu")
    assert response.expires_in_seconds == 600
    assert repository.challenge is not None
    assert len(email_gateway.messages) == 1
    sent_code = email_gateway.messages[0][2]
    assert sent_code.isdigit() and len(sent_code) == 6
    assert repository.challenge.code_hash != sent_code


@pytest.mark.asyncio
async def test_unknown_account_receives_neutral_response_without_email() -> None:
    service, _, email_gateway = make_service(account_exists=False)
    response = await service.request("87654321@students.hebron.edu")
    assert response.message == "If the account exists, a reset code has been sent."
    assert email_gateway.messages == []


@pytest.mark.asyncio
async def test_correct_code_issues_one_time_reset_token_and_changes_password() -> None:
    service, repository, email_gateway = make_service()
    await service.request(repository.email)
    result = await service.verify(repository.email, email_gateway.messages[0][2])
    assert result.reset_token
    assert repository.reset_token_hash != result.reset_token
    await service.confirm(repository.email, result.reset_token, "new-secure-password")
    assert repository.new_password_hash is not None
    assert Pbkdf2PasswordHasher().verify("new-secure-password", repository.new_password_hash)


@pytest.mark.asyncio
async def test_wrong_expired_and_exhausted_codes_are_rejected() -> None:
    service, repository, email_gateway = make_service()
    await service.request(repository.email)
    with pytest.raises(PasswordResetCodeInvalidError):
        await service.verify(repository.email, "000000")
    assert repository.challenge and repository.challenge.attempts == 1
    repository.challenge.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    with pytest.raises(PasswordResetCodeExpiredError):
        await service.verify(repository.email, email_gateway.messages[0][2])
    repository.challenge.expires_at = datetime.now(timezone.utc) + timedelta(minutes=1)
    repository.challenge.attempts = repository.challenge.max_attempts
    with pytest.raises(PasswordResetAttemptsExceededError):
        await service.verify(repository.email, email_gateway.messages[0][2])


@pytest.mark.asyncio
async def test_invalid_reset_token_cannot_change_password() -> None:
    service, repository, _ = make_service()
    with pytest.raises(PasswordResetTokenInvalidError):
        await service.confirm(repository.email, "invalid-reset-token-value-123456", "new-password")
    assert repository.new_password_hash is None


@pytest.mark.asyncio
async def test_password_reset_hourly_lock_is_neutral_and_sends_no_email() -> None:
    user = make_user()
    repository = FakeResetRepository(user.email)
    email_gateway = FakeEmailGateway()
    rate_limit = FakeRateLimitRepository(
        EmailCodeRateDecision(
            allowed=False,
            retry_after_seconds=1800,
            hourly_limit_reached=True,
        )
    )
    service = PasswordResetService(
        FakeAuthenticationRepository(user),
        repository,
        email_gateway,
        Pbkdf2PasswordHasher(),
        SECRET,
        rate_limit_repository=rate_limit,
    )

    response = await service.request(user.email)

    assert response.message == "If the account exists, a reset code has been sent."
    assert response.hourly_limit_reached is True
    assert response.resend_after_seconds == 1800
    assert len(rate_limit.identifier_hash) == 64
    assert email_gateway.messages == []
