from typing import Protocol
from uuid import UUID

from src.entities.dto.registration import RegisteredUser, UserProfileCreate


class AuthUserGateway(Protocol):
    async def create_user(self, email: str, password: str) -> UUID: ...

    async def delete_user(self, user_id: UUID) -> None: ...


class UserProfileRepository(Protocol):
    async def create(self, profile: UserProfileCreate) -> RegisteredUser: ...
