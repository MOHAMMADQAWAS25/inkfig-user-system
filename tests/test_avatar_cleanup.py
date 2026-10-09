from datetime import UTC, datetime

import pytest

from src.app.services.avatar_cleanup_service import AvatarCleanupService
from src.entities.exceptions.profile_avatar import AvatarStorageError
from src.entities.repositories.avatar_cleanup import AvatarCleanupJob


class CleanupRepositoryStub:
    def __init__(self, jobs: list[AvatarCleanupJob]) -> None:
        self.jobs = jobs
        self.completed: list[str] = []
        self.rescheduled: list[tuple[str, int, str]] = []

    async def list_due(self, now: datetime, limit: int) -> list[AvatarCleanupJob]:
        assert now.tzinfo == UTC
        return self.jobs[:limit]

    async def complete(self, object_path: str) -> None:
        self.completed.append(object_path)

    async def reschedule(
        self,
        object_path: str,
        attempts: int,
        next_attempt_at: datetime,
        last_error: str,
    ) -> None:
        assert next_attempt_at > datetime.now(UTC)
        self.rescheduled.append((object_path, attempts, last_error))


class CleanupStorageStub:
    def __init__(self, failing: set[str] | None = None) -> None:
        self.failing = failing or set()
        self.deleted: list[str] = []

    async def create_signed_upload(self, path: str) -> tuple[str, str]:
        raise NotImplementedError

    async def object_is_valid(
        self, path: str, allowed_types: set[str], max_bytes: int
    ) -> bool:
        raise NotImplementedError

    async def delete(self, path: str) -> None:
        if path in self.failing:
            raise AvatarStorageError
        self.deleted.append(path)

    def public_url(self, path: str) -> str:
        raise NotImplementedError


@pytest.mark.asyncio
async def test_cleanup_deletes_objects_and_completes_jobs() -> None:
    repository = CleanupRepositoryStub([AvatarCleanupJob("user/old.jpg", 0)])
    storage = CleanupStorageStub()

    result = await AvatarCleanupService(repository, storage).run()

    assert result.deleted == 1
    assert result.deferred == 0
    assert storage.deleted == ["user/old.jpg"]
    assert repository.completed == ["user/old.jpg"]


@pytest.mark.asyncio
async def test_cleanup_reschedules_failed_storage_deletion() -> None:
    repository = CleanupRepositoryStub([AvatarCleanupJob("user/old.jpg", 2)])
    storage = CleanupStorageStub({"user/old.jpg"})

    result = await AvatarCleanupService(repository, storage).run()

    assert result.deleted == 0
    assert result.deferred == 1
    assert repository.completed == []
    assert repository.rescheduled == [
        ("user/old.jpg", 3, "Avatar storage deletion failed.")
    ]
