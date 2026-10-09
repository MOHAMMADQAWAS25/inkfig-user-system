from typing import ClassVar
from uuid import UUID, uuid4

from src.entities.dto.profile_avatar import (
    AvatarResponse,
    AvatarUploadRequest,
    AvatarUploadResponse,
)
from src.entities.exceptions.profile_avatar import (
    AvatarStorageError,
    AvatarUploadNotFoundError,
    UnsupportedAvatarError,
)
from src.entities.repositories.profile_avatar import (
    ProfileAvatarRepository,
    ProfileAvatarStorage,
)


class ProfileAvatarService:
    ALLOWED: ClassVar[dict[str, str]] = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    def __init__(
        self, repository: ProfileAvatarRepository, storage: ProfileAvatarStorage
    ) -> None:
        self._repository, self._storage = repository, storage

    async def prepare_upload(
        self, user_id: UUID, data: AvatarUploadRequest
    ) -> AvatarUploadResponse:
        extension = self.ALLOWED.get(data.mime_type)
        if extension is None:
            raise UnsupportedAvatarError
        path = f"{user_id}/{uuid4()}{extension}"
        upload_url, token = await self._storage.create_signed_upload(path)
        return AvatarUploadResponse(
            object_path=path, upload_url=upload_url, upload_token=token
        )

    async def complete_upload(self, user_id: UUID, object_path: str) -> AvatarResponse:
        if not object_path.startswith(
            f"{user_id}/"
        ) or not await self._storage.object_is_valid(
            object_path, set(self.ALLOWED), 2 * 1024 * 1024
        ):
            raise AvatarUploadNotFoundError
        previous = await self._repository.replace_avatar(user_id, object_path)
        if previous and previous != object_path:
            try:
                await self._storage.delete(previous)
            except AvatarStorageError:
                pass
        return AvatarResponse(avatar_url=self._storage.public_url(object_path))

    async def remove(self, user_id: UUID) -> None:
        previous = await self._repository.get_avatar(user_id)
        if previous:
            await self._storage.delete(previous)
        await self._repository.clear_avatar(user_id)
