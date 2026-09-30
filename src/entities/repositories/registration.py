from typing import Protocol
from uuid import UUID

from datetime import datetime

from src.entities.dto.registration import (
    EmailVerificationCreate,
    PendingEmailVerification,
    RegisteredUser,
    UserProfileCreate,
)


class PasswordHasher(Protocol):
    def hash(self, password: str) -> str: ...

    def verify(self, password: str, encoded: str) -> bool: ...


class UserProfileRepository(Protocol):
    async def get_recoverable_legacy_user_id(self, email: str) -> UUID | None: ...

    async def create_pending(
        self, profile: UserProfileCreate, verification: EmailVerificationCreate
    ) -> RegisteredUser: ...

    async def get_pending_verification(
        self, email: str
    ) -> PendingEmailVerification | None: ...

    async def record_failed_attempt(self, verification_id: UUID) -> None: ...

    async def activate_verified_user(
        self, verification_id: UUID, user_id: UUID, verified_at: datetime
    ) -> None: ...

    async def replace_verification(
        self, previous_id: UUID, verification: EmailVerificationCreate
    ) -> None: ...

    async def restart_legacy_account(
        self, profile: UserProfileCreate, verification: EmailVerificationCreate
    ) -> None: ...


class VerificationEmailGateway(Protocol):
    async def send_verification_code(
        self, email: str, full_name: str, code: str, expires_minutes: int
    ) -> None: ...
