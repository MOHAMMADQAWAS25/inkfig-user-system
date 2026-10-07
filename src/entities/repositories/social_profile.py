from typing import Protocol
from uuid import UUID

from src.entities.dto.social_profile import (
    ProfileAccountSummary,
    ProfileSearchResult,
    PublicProfileResponse,
)


class SocialProfileRepository(Protocol):
    async def search_profiles(
        self, query: str, limit: int
    ) -> list[ProfileSearchResult]: ...

    async def get_profile(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> PublicProfileResponse | None: ...

    async def list_followers(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> list[ProfileAccountSummary] | None: ...

    async def list_following(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> list[ProfileAccountSummary] | None: ...

    async def set_follow(
        self, follower_user_id: UUID, followed_user_id: UUID, following: bool
    ) -> bool: ...

