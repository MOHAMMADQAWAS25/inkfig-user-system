from typing import Protocol
from uuid import UUID

from datetime import datetime

from src.entities.dto.registration import (
    EmailVerificationCreate,
    PendingEmailVerification,
    RegisteredUser,
    UserProfileCreate,
)


class AuthUserGateway(Protocol):
    async def create_user(self, email: str, password: str) -> UUID: ...

    async def delete_user(self, user_id: UUID) -> None: ...

    async def confirm_email(self, user_id: UUID) -> None: ...


class UserProfileRepository(Protocol):
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


class VerificationEmailGateway(Protocol):
    async def send_verification_code(
        self, email: str, full_name: str, code: str, expires_minutes: int
    ) -> None: ...
