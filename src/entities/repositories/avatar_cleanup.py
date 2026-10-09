from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class AvatarCleanupJob:
    object_path: str
    attempts: int


class AvatarCleanupRepository(Protocol):
    async def list_due(self, now: datetime, limit: int) -> list[AvatarCleanupJob]: ...
    async def complete(self, object_path: str) -> None: ...
    async def reschedule(
        self,
        object_path: str,
        attempts: int,
        next_attempt_at: datetime,
        last_error: str,
    ) -> None: ...
