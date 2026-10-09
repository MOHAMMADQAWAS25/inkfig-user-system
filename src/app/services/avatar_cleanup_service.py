from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from src.entities.exceptions.profile_avatar import AvatarStorageError
from src.entities.repositories.avatar_cleanup import AvatarCleanupRepository
from src.entities.repositories.profile_avatar import ProfileAvatarStorage


@dataclass(frozen=True)
class AvatarCleanupResult:
    processed: int
    deleted: int
    deferred: int


class AvatarCleanupService:
    def __init__(
        self,
        repository: AvatarCleanupRepository,
        storage: ProfileAvatarStorage,
    ) -> None:
        self._repository = repository
        self._storage = storage

    async def run(self, limit: int = 50) -> AvatarCleanupResult:
        now = datetime.now(UTC)
        jobs = await self._repository.list_due(now, limit)
        deleted = 0
        deferred = 0
        for job in jobs:
            try:
                await self._storage.delete(job.object_path)
            except AvatarStorageError:
                attempts = job.attempts + 1
                delay_minutes = min(2 ** min(attempts, 10), 24 * 60)
                await self._repository.reschedule(
                    job.object_path,
                    attempts,
                    now + timedelta(minutes=delay_minutes),
                    "Avatar storage deletion failed.",
                )
                deferred += 1
            else:
                await self._repository.complete(job.object_path)
                deleted += 1
        return AvatarCleanupResult(len(jobs), deleted, deferred)
