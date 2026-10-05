from datetime import datetime, timezone
from uuid import UUID, uuid4

import jwt
import pytest

from src.app.services.authentication_service import AuthenticationService
from src.entities.dto.authentication import AuthenticatedUser
from src.entities.exceptions.authentication import (
    AccountInactiveError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from src.infrastructure.security.passwords import Pbkdf2PasswordHasher
from src.entities.enums.account_status import AccountStatus
from src.entities.exceptions.authentication import AccountAdminSuspendedError


class FakeAuthenticationRepository:
    def __init__(self, user: AuthenticatedUser | None) -> None:
        self.user = user
        self.tokens: dict[str, tuple[UUID, datetime]] = {}

    async def find_user_by_email(self, email: str) -> AuthenticatedUser | None:
        return self.user if self.user and self.user.email == email else None

    async def store_refresh_token(
        self, token_id: UUID, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        self.tokens[token_hash] = (user_id, expires_at)

    async def reactivate_self_deactivated(self, user_id: UUID) -> AuthenticatedUser:
        assert self.user is not None and self.user.user_id == user_id
        self.user = self.user.model_copy(update={"is_active": True, "account_status": AccountStatus.ACTIVE})
        return self.user

    async def consume_refresh_token(
        self, token_hash: str, consumed_at: datetime
    ) -> AuthenticatedUser | None:
        record = self.tokens.pop(token_hash, None)
        if record is None or record[1] <= consumed_at:
            return None
        return self.user

    async def revoke_refresh_token(self, token_hash: str, revoked_at: datetime) -> None:
        self.tokens.pop(token_hash, None)


def make_user(*, active: bool = True) -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id=uuid4(),
        email="12345678@students.hebron.edu",
        full_name="Student Name",
        password_hash=Pbkdf2PasswordHasher().hash("correct-password"),
        is_active=active,
        email_verified_at=datetime.now(timezone.utc) if active else None,
        token_version=0,
    )


def make_service(repository: FakeAuthenticationRepository) -> AuthenticationService:
    return AuthenticationService(
        repository,
        Pbkdf2PasswordHasher(),
        "a-long-test-jwt-secret-with-32-bytes-minimum",
        "inkfig-user-system",
    )


def test_password_hash_is_salted_and_verifiable() -> None:
    hasher = Pbkdf2PasswordHasher()
    first = hasher.hash("correct-password")
    second = hasher.hash("correct-password")
    assert first != second
    assert hasher.verify("correct-password", first)
    assert not hasher.verify("wrong-password", first)


@pytest.mark.asyncio
async def test_login_issues_inkfig_access_and_refresh_tokens() -> None:
    user = make_user()
    repository = FakeAuthenticationRepository(user)
    result = await make_service(repository).login(user.email, "correct-password")
    claims = jwt.decode(
        result.access_token,
        "a-long-test-jwt-secret-with-32-bytes-minimum",
        algorithms=["HS256"],
        issuer="inkfig-user-system",
    )
    assert claims["sub"] == str(user.user_id)
    assert claims["type"] == "access"
    assert result.refresh_token != result.access_token
    assert len(repository.tokens) == 1


@pytest.mark.asyncio
async def test_login_rejects_wrong_password_and_inactive_account() -> None:
    user = make_user()
    with pytest.raises(InvalidCredentialsError):
        await make_service(FakeAuthenticationRepository(user)).login(user.email, "wrong-password")
    inactive = make_user(active=False)
    with pytest.raises(AccountInactiveError):
        await make_service(FakeAuthenticationRepository(inactive)).login(
            inactive.email, "correct-password"
        )

@pytest.mark.asyncio
async def test_login_reactivates_only_self_deactivated_accounts() -> None:
    self_deactivated = make_user(active=False).model_copy(update={"email_verified_at": datetime.now(timezone.utc), "account_status": AccountStatus.SELF_DEACTIVATED})
    result = await make_service(FakeAuthenticationRepository(self_deactivated)).login(self_deactivated.email, "correct-password")
    assert result.user_id == self_deactivated.user_id
    admin_suspended = make_user(active=False).model_copy(update={"email_verified_at": datetime.now(timezone.utc), "account_status": AccountStatus.ADMIN_SUSPENDED})
    with pytest.raises(AccountAdminSuspendedError):
        await make_service(FakeAuthenticationRepository(admin_suspended)).login(admin_suspended.email, "correct-password")


@pytest.mark.asyncio
async def test_refresh_token_is_rotated_and_cannot_be_reused() -> None:
    user = make_user()
    repository = FakeAuthenticationRepository(user)
    service = make_service(repository)
    first = await service.login(user.email, "correct-password")
    second = await service.refresh(first.refresh_token)
    assert second.refresh_token != first.refresh_token
    with pytest.raises(InvalidRefreshTokenError):
        await service.refresh(first.refresh_token)
