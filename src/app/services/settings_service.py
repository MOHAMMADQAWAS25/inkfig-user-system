from uuid import UUID

from src.entities.dto.settings import ChangePasswordRequest, ProfileSettingsResponse, UpdateProfileSettingsRequest
from src.entities.exceptions.settings import CurrentPasswordInvalidError, ProfileNotFoundError
from src.entities.repositories.registration import PasswordHasher
from src.entities.repositories.settings import SettingsRepository


class SettingsService:
    def __init__(self, repository: SettingsRepository, password_hasher: PasswordHasher) -> None:
        self._repository = repository
        self._password_hasher = password_hasher

    async def get_profile(self, user_id: UUID) -> ProfileSettingsResponse:
        profile = await self._repository.get_profile(user_id)
        if profile is None:
            raise ProfileNotFoundError
        return profile

    async def update_profile(self, user_id: UUID, request: UpdateProfileSettingsRequest) -> ProfileSettingsResponse:
        return await self._repository.update_profile(user_id, request)

    async def change_password(self, user_id: UUID, request: ChangePasswordRequest) -> None:
        password_hash = await self._repository.get_password_hash(user_id)
        if password_hash is None or not self._password_hasher.verify(request.current_password, password_hash):
            raise CurrentPasswordInvalidError
        await self._repository.update_password(user_id, self._password_hasher.hash(request.password))

    async def deactivate(self, user_id: UUID, current_password: str) -> None:
        password_hash = await self._repository.get_password_hash(user_id)
        if password_hash is None or not self._password_hasher.verify(current_password, password_hash):
            raise CurrentPasswordInvalidError
        await self._repository.set_active(user_id, False)
