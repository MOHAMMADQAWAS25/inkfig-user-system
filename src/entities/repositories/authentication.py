from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.entities.dto.authentication import AuthenticatedUser


class AuthenticationRepository(Protocol):
    async def find_user_by_email(self, email: str) -> AuthenticatedUser | None: ...

    async def store_refresh_token(
        self, token_id: UUID, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None: ...

    async def consume_refresh_token(
        self, token_hash: str, consumed_at: datetime
    ) -> AuthenticatedUser | None: ...

    async def revoke_refresh_token(self, token_hash: str, revoked_at: datetime) -> None: ...
