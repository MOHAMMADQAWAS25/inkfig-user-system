from uuid import UUID, uuid4

import pytest

from src.app.services.profile_avatar_service import ProfileAvatarService
from src.entities.dto.profile_avatar import AvatarUploadRequest
from src.entities.exceptions.profile_avatar import AvatarUploadNotFoundError, UnsupportedAvatarError


class AvatarRepositoryStub:
    def __init__(self) -> None:
        self.saved: tuple[UUID, str] | None = None
        self.previous: str | None = None

    async def replace_avatar(self, user_id: UUID, object_path: str) -> str | None:
        self.saved = (user_id, object_path)
        return self.previous


class AvatarStorageStub:
    def __init__(self) -> None:
        self.exists = True
        self.deleted: list[str] = []

    async def create_signed_upload(self, path: str) -> tuple[str, str]:
        return f"https://upload.test/{path}?token=signed", "signed"

    async def object_is_valid(self, path: str, allowed_types: set[str], max_bytes: int) -> bool:
        assert allowed_types == {"image/jpeg", "image/png", "image/webp"}
        assert max_bytes == 2 * 1024 * 1024
        return self.exists

    async def delete(self, path: str) -> None:
        self.deleted.append(path)

    def public_url(self, path: str) -> str:
        return f"https://cdn.test/{path}"


@pytest.mark.asyncio
async def test_avatar_upload_is_scoped_to_user_and_replaces_previous_object() -> None:
    repository = AvatarRepositoryStub()
    storage = AvatarStorageStub()
    service = ProfileAvatarService(repository, storage)
    user_id = uuid4()
    upload = await service.prepare_upload(
        user_id,
        AvatarUploadRequest(file_name="portrait.png", mime_type="image/png", file_size=1024),
    )
    assert upload.object_path.startswith(f"{user_id}/")
    repository.previous = f"{user_id}/old.png"
    result = await service.complete_upload(user_id, upload.object_path)
    assert repository.saved == (user_id, upload.object_path)
    assert storage.deleted == [f"{user_id}/old.png"]
    assert result.avatar_url == f"https://cdn.test/{upload.object_path}"


@pytest.mark.asyncio
async def test_avatar_rejects_unsupported_content_type_and_foreign_path() -> None:
    service = ProfileAvatarService(AvatarRepositoryStub(), AvatarStorageStub())
    user_id = uuid4()
    with pytest.raises(UnsupportedAvatarError):
        await service.prepare_upload(
            user_id,
            AvatarUploadRequest(file_name="avatar.gif", mime_type="image/gif", file_size=10),
        )
    with pytest.raises(AvatarUploadNotFoundError):
        await service.complete_upload(user_id, f"{uuid4()}/avatar.png")
