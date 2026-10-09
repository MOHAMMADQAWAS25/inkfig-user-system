from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.postgres.models.user_profile import (
    AvatarStorageCleanupJobModel,
    UserProfileModel,
)


class SqlAlchemyProfileAvatarRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def replace_avatar(self, user_id: UUID, object_path: str) -> str | None:
        previous = await self._session.scalar(
            select(UserProfileModel.avatar_object_path).where(
                UserProfileModel.user_id == user_id
            ).with_for_update()
        )
        await self._session.execute(
            update(UserProfileModel)
            .where(UserProfileModel.user_id == user_id)
            .values(avatar_object_path=object_path)
        )
        if previous and previous != object_path:
            await self._session.execute(
                insert(AvatarStorageCleanupJobModel)
                .values(object_path=previous)
                .on_conflict_do_nothing(index_elements=["object_path"])
            )
        await self._session.commit()
        return previous

    async def complete_cleanup(self, object_path: str) -> None:
        await self._session.execute(
            delete(AvatarStorageCleanupJobModel).where(
                AvatarStorageCleanupJobModel.object_path == object_path
            )
        )
        await self._session.commit()

    async def get_avatar(self, user_id: UUID) -> str | None:
        return await self._session.scalar(
            select(UserProfileModel.avatar_object_path).where(
                UserProfileModel.user_id == user_id
            )
        )

    async def clear_avatar(self, user_id: UUID) -> None:
        await self._session.execute(
            update(UserProfileModel)
            .where(UserProfileModel.user_id == user_id)
            .values(avatar_object_path=None)
        )
        await self._session.commit()
