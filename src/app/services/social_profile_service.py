from uuid import UUID

from src.entities.dto.social_profile import (
    ProfileAccountSummary,
    PublicProfileResponse,
)
from src.entities.exceptions.social_profile import (
    CannotFollowSelfError,
    ProfileNotFoundError,
)
from src.entities.repositories.social_profile import SocialProfileRepository


class SocialProfileService:
    def __init__(self, repository: SocialProfileRepository) -> None:
        self._repository = repository

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

