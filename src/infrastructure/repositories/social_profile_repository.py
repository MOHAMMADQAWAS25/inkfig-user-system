from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.social_profile import (
    ProfileAccountSummary,
    ProfileSearchResult,
    PublicProfileResponse,
)
from src.entities.repositories.profile_avatar import ProfileAvatarStorage


class SqlAlchemySocialProfileRepository:
    def __init__(self, session: AsyncSession, storage: ProfileAvatarStorage) -> None:
        self._session, self._storage = session, storage

    async def search_profiles(
        self, query: str, limit: int
    ) -> list[ProfileSearchResult]:
        rows = (
            await self._session.execute(
                text(
                    """
                    select p.user_id, p.full_name
                    from user_profiles p
                    join user_accounts a on a.user_id = p.user_id
                    where p.is_active = true
                      and a.account_status = 'active'
                      and a.email_verified_at is not null
                      and lower(p.full_name) like '%' || lower(:query) || '%'
                    order by
                      case when lower(p.full_name) like lower(:query) || '%' then 0 else 1 end,
                      lower(p.full_name), p.user_id
                    limit :limit
                    """
                ),
                {"query": query, "limit": limit},
            )
        ).mappings()
        return [
            ProfileSearchResult(user_id=row.user_id, full_name=row.full_name)
            for row in rows
        ]

    async def get_profile(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> PublicProfileResponse | None:
        row = (
            await self._session.execute(
                text(
                    """
                    select
                        p.user_id,
                        p.full_name,
                        p.avatar_object_path,
                        (select count(*) from user_follows f join user_accounts fa on fa.user_id = f.follower_user_id
                         where f.followed_user_id = p.user_id and fa.account_status = 'active') as follower_count,
                        (select count(*) from user_follows f join user_accounts fa on fa.user_id = f.followed_user_id
                         where f.follower_user_id = p.user_id and fa.account_status = 'active') as following_count,
                        (select count(*)
                         from works w join work_likes l on l.work_id = w.work_id join user_accounts la on la.user_id = l.user_id
                         where w.owner_user_id = p.user_id
                           and w.status = 'published' and la.account_status = 'active') as like_count,
                        exists (
                            select 1 from user_follows f
                            where f.follower_user_id = :viewer_user_id
                              and f.followed_user_id = p.user_id
                        ) as is_following
                    from user_profiles p
                    join user_accounts a on a.user_id = p.user_id
                    where p.user_id = :profile_user_id
                      and p.is_active = true
                      and a.account_status = 'active'
                      and a.email_verified_at is not null
                    """
                ),
                {
                    "profile_user_id": profile_user_id,
                    "viewer_user_id": viewer_user_id,
                },
            )
        ).mappings().first()
        if row is None:
            return None
        return PublicProfileResponse(
            user_id=row.user_id,
            full_name=row.full_name,
            avatar_url=self._storage.public_url(row.avatar_object_path) if row.avatar_object_path else None,
            follower_count=row.follower_count,
            following_count=row.following_count,
            like_count=row.like_count,
            is_following=row.is_following,
            is_self=row.user_id == viewer_user_id,
        )

    async def list_followers(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> list[ProfileAccountSummary] | None:
        return await self._list_connections(
            profile_user_id, viewer_user_id, followers=True
        )

    async def list_following(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> list[ProfileAccountSummary] | None:
        return await self._list_connections(
            profile_user_id, viewer_user_id, followers=False
        )

    async def _list_connections(
        self, profile_user_id: UUID, viewer_user_id: UUID, *, followers: bool
    ) -> list[ProfileAccountSummary] | None:
        exists = await self._session.scalar(
            text(
                """
                select exists(
                    select 1 from user_accounts
                    where user_id = :profile_user_id
                      and account_status = 'active'
                      and email_verified_at is not null
                )
                """
            ),
            {"profile_user_id": profile_user_id},
        )
        if not exists:
            return None
        account_column = "f.follower_user_id" if followers else "f.followed_user_id"
        scope_column = "f.followed_user_id" if followers else "f.follower_user_id"
        rows = (
            await self._session.execute(
                text(
                    f"""
                    select
                        p.user_id,
                        p.full_name,
                        p.avatar_object_path,
                        exists (
                            select 1 from user_follows mine
                            where mine.follower_user_id = :viewer_user_id
                              and mine.followed_user_id = p.user_id
                        ) as is_following
                    from user_follows f
                    join user_profiles p on p.user_id = {account_column}
                    join user_accounts a on a.user_id = p.user_id
                    where {scope_column} = :profile_user_id
                      and p.is_active = true
                      and a.account_status = 'active'
                      and a.email_verified_at is not null
                    order by f.created_at desc, p.user_id
                    """
                ),
                {
                    "profile_user_id": profile_user_id,
                    "viewer_user_id": viewer_user_id,
                },
            )
        ).mappings()
        return [
            ProfileAccountSummary(
                user_id=row.user_id,
                full_name=row.full_name,
                avatar_url=self._storage.public_url(row.avatar_object_path) if row.avatar_object_path else None,
                is_following=row.is_following,
            )
            for row in rows
        ]

    async def set_follow(
        self, follower_user_id: UUID, followed_user_id: UUID, following: bool
    ) -> bool:
        target_exists = await self._session.scalar(
            text(
                """
                select exists(
                    select 1 from user_accounts
                    where user_id = :followed_user_id
                      and account_status = 'active'
                      and email_verified_at is not null
                )
                """
            ),
            {"followed_user_id": followed_user_id},
        )
        if not target_exists:
            return False
        if following:
            await self._session.execute(
                text(
                    """
                    insert into user_follows (follower_user_id, followed_user_id)
                    values (:follower_user_id, :followed_user_id)
                    on conflict do nothing
                    """
                ),
                {
                    "follower_user_id": follower_user_id,
                    "followed_user_id": followed_user_id,
                },
            )
        else:
            await self._session.execute(
                text(
                    """
                    delete from user_follows
                    where follower_user_id = :follower_user_id
                      and followed_user_id = :followed_user_id
                    """
                ),
                {
                    "follower_user_id": follower_user_id,
                    "followed_user_id": followed_user_id,
                },
            )
        await self._session.commit()
        return True

