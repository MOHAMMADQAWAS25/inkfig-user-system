from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.entities.dto.authentication import PasswordResetChallenge


class PasswordResetRepository(Protocol):
    async def create_challenge(
        self, user_id: UUID, code_hash: str, expires_at: datetime, max_attempts: int
    ) -> None: ...

    async def get_pending(self, email: str) -> PasswordResetChallenge | None: ...

    async def record_failed_attempt(self, challenge_id: UUID) -> None: ...

    async def verify_challenge(
        self, challenge_id: UUID, token_hash: str, token_expires_at: datetime, verified_at: datetime
    ) -> None: ...

    async def reset_password(
        self, email: str, token_hash: str, password_hash: str, now: datetime
    ) -> bool: ...


class PasswordResetEmailGateway(Protocol):
    async def send_password_reset_code(
        self, email: str, full_name: str, code: str, expires_minutes: int
    ) -> None: ...
