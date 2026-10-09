from datetime import datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.repositories.avatar_cleanup import AvatarCleanupJob
from src.infrastructure.db.postgres.models.user_profile import (
    AvatarStorageCleanupJobModel,
)


class SqlAlchemyAvatarCleanupRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_due(self, now: datetime, limit: int) -> list[AvatarCleanupJob]:
        rows = (
            await self._session.execute(
                select(AvatarStorageCleanupJobModel)
                .where(AvatarStorageCleanupJobModel.next_attempt_at <= now)
                .order_by(
                    AvatarStorageCleanupJobModel.next_attempt_at,
                    AvatarStorageCleanupJobModel.created_at,
                )
                .limit(limit)
            )
        ).scalars()
        return [AvatarCleanupJob(row.object_path, row.attempts) for row in rows]

    async def complete(self, object_path: str) -> None:
        await self._session.execute(
            delete(AvatarStorageCleanupJobModel).where(
                AvatarStorageCleanupJobModel.object_path == object_path
            )
        )
        await self._session.commit()

    async def reschedule(
        self,
        object_path: str,
        attempts: int,
        next_attempt_at: datetime,
        last_error: str,
    ) -> None:
        await self._session.execute(
            update(AvatarStorageCleanupJobModel)
            .where(AvatarStorageCleanupJobModel.object_path == object_path)
            .values(
                attempts=attempts,
                next_attempt_at=next_attempt_at,
                last_error=last_error,
                updated_at=datetime.now(next_attempt_at.tzinfo),
            )
        )
        await self._session.commit()
