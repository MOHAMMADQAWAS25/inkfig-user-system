from uuid import UUID

from src.app.services.profile_avatar_service import ProfileAvatarService
from src.entities.dto.profile_avatar import (
    AvatarResponse,
    AvatarUploadRequest,
    AvatarUploadResponse,
)
from src.entities.dto.social_profile import (
    ProfileAccountSummary,
    ProfileSearchResult,
    PublicProfileResponse,
)
from src.entities.exceptions.social_profile import (
    CannotFollowSelfError,
    ProfileNotFoundError,
)
from src.entities.repositories.social_profile import SocialProfileRepository


class SocialProfileService:
    def __init__(
        self,
        repository: SocialProfileRepository,
        avatar_service: ProfileAvatarService | None = None,
    ) -> None:
        self._repository = repository
        self._avatar_service = avatar_service

    async def prepare_avatar_upload(
        self, user_id: UUID, data: AvatarUploadRequest
    ) -> AvatarUploadResponse:
        if self._avatar_service is None:
            raise RuntimeError("Avatar uploads are not configured.")
        return await self._avatar_service.prepare_upload(user_id, data)

    async def complete_avatar_upload(
        self, user_id: UUID, object_path: str
    ) -> AvatarResponse:
        if self._avatar_service is None:
            raise RuntimeError("Avatar uploads are not configured.")
        return await self._avatar_service.complete_upload(user_id, object_path)

    async def remove_avatar(self, user_id: UUID) -> None:
        if self._avatar_service is None:
            raise RuntimeError("Avatar storage is not configured.")
        await self._avatar_service.remove(user_id)

    async def search_profiles(
        self, query: str, limit: int, cursor: int
    ) -> tuple[list[ProfileSearchResult], int | None]:
        normalized = " ".join(query.split())
        items = await self._repository.search_profiles(normalized, limit + 1, cursor)
        next_cursor = cursor + limit if len(items) > limit else None
        return items[:limit], next_cursor

    async def get_profile(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> PublicProfileResponse:
        profile = await self._repository.get_profile(profile_user_id, viewer_user_id)
        if profile is None:
            raise ProfileNotFoundError
        return profile

    async def list_followers(
        self, profile_user_id: UUID, viewer_user_id: UUID, limit: int, cursor: int
    ) -> tuple[list[ProfileAccountSummary], int | None]:
        accounts = await self._repository.list_followers(
            profile_user_id, viewer_user_id, limit + 1, cursor
        )
        if accounts is None:
            raise ProfileNotFoundError
        return accounts[:limit], cursor + limit if len(accounts) > limit else None

    async def list_following(
        self, profile_user_id: UUID, viewer_user_id: UUID, limit: int, cursor: int
    ) -> tuple[list[ProfileAccountSummary], int | None]:
        accounts = await self._repository.list_following(
            profile_user_id, viewer_user_id, limit + 1, cursor
        )
        if accounts is None:
            raise ProfileNotFoundError
        return accounts[:limit], cursor + limit if len(accounts) > limit else None

    async def set_follow(
        self, follower_user_id: UUID, followed_user_id: UUID, following: bool
    ) -> None:
        if follower_user_id == followed_user_id:
            raise CannotFollowSelfError
        if not await self._repository.set_follow(
            follower_user_id, followed_user_id, following
        ):
            raise ProfileNotFoundError
