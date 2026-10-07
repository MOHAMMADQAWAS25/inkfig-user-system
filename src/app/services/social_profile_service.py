from uuid import UUID

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
from src.app.services.profile_avatar_service import ProfileAvatarService
from src.entities.dto.profile_avatar import AvatarResponse, AvatarUploadRequest, AvatarUploadResponse


class SocialProfileService:
    def __init__(self, repository: SocialProfileRepository, avatar_service: ProfileAvatarService | None = None) -> None:
        self._repository = repository
        self._avatar_service = avatar_service

    async def prepare_avatar_upload(self, user_id: UUID, data: AvatarUploadRequest) -> AvatarUploadResponse:
        if self._avatar_service is None:
            raise RuntimeError("Avatar uploads are not configured.")
        return await self._avatar_service.prepare_upload(user_id, data)

    async def complete_avatar_upload(self, user_id: UUID, object_path: str) -> AvatarResponse:
        if self._avatar_service is None:
            raise RuntimeError("Avatar uploads are not configured.")
        return await self._avatar_service.complete_upload(user_id, object_path)

    async def search_profiles(self, query: str, limit: int) -> list[ProfileSearchResult]:
        normalized = " ".join(query.split())
        return await self._repository.search_profiles(normalized, limit)

    async def get_profile(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> PublicProfileResponse:
        profile = await self._repository.get_profile(profile_user_id, viewer_user_id)
        if profile is None:
            raise ProfileNotFoundError
        return profile

    async def list_followers(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> list[ProfileAccountSummary]:
        accounts = await self._repository.list_followers(
            profile_user_id, viewer_user_id
        )
        if accounts is None:
            raise ProfileNotFoundError
        return accounts

    async def list_following(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> list[ProfileAccountSummary]:
        accounts = await self._repository.list_following(
            profile_user_id, viewer_user_id
        )
        if accounts is None:
            raise ProfileNotFoundError
        return accounts

    async def set_follow(
        self, follower_user_id: UUID, followed_user_id: UUID, following: bool
    ) -> None:
        if follower_user_id == followed_user_id:
            raise CannotFollowSelfError
        if not await self._repository.set_follow(
            follower_user_id, followed_user_id, following
        ):
            raise ProfileNotFoundError

