from uuid import UUID, uuid4

import pytest

from src.app.services.social_profile_service import SocialProfileService
from src.entities.dto.social_profile import (
    ProfileAccountSummary,
    ProfileSearchResult,
    PublicProfileResponse,
)
from src.entities.exceptions.social_profile import (
    CannotFollowSelfError,
    ProfileNotFoundError,
)


class SocialProfileRepositoryStub:
    def __init__(self) -> None:
        self.profile_id = uuid4()
        self.follow_calls: list[tuple[object, object, bool]] = []
        self.available = True
        self.search_query: str | None = None

    async def get_profile(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> PublicProfileResponse | None:
        if not self.available:
            return None
        return PublicProfileResponse(
            user_id=profile_user_id,
            full_name="InkFig Artist",
            avatar_url=None,
            follower_count=3,
            following_count=2,
            like_count=9,
            is_following=False,
            is_self=profile_user_id == viewer_user_id,
        )

    async def search_profiles(
        self, query: str, limit: int
    ) -> list[ProfileSearchResult]:
        self.search_query = query
        return [ProfileSearchResult(user_id=self.profile_id, full_name="InkFig Artist")][
            :limit
        ]

    async def list_followers(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> list[ProfileAccountSummary] | None:
        return [] if self.available else None

    async def list_following(
        self, profile_user_id: UUID, viewer_user_id: UUID
    ) -> list[ProfileAccountSummary] | None:
        return [] if self.available else None

    async def set_follow(
        self, follower_user_id: UUID, followed_user_id: UUID, following: bool
    ) -> bool:
        self.follow_calls.append((follower_user_id, followed_user_id, following))
        return self.available


@pytest.mark.asyncio
async def test_follow_and_unfollow_are_scoped_to_authenticated_user() -> None:
    repository = SocialProfileRepositoryStub()
    service = SocialProfileService(repository)
    viewer_id = uuid4()

    await service.set_follow(viewer_id, repository.profile_id, True)
    await service.set_follow(viewer_id, repository.profile_id, False)

    assert repository.follow_calls == [
        (viewer_id, repository.profile_id, True),
        (viewer_id, repository.profile_id, False),
    ]


@pytest.mark.asyncio
async def test_user_cannot_follow_self() -> None:
    repository = SocialProfileRepositoryStub()
    service = SocialProfileService(repository)
    viewer_id = uuid4()

    with pytest.raises(CannotFollowSelfError):
        await service.set_follow(viewer_id, viewer_id, True)

    assert repository.follow_calls == []


@pytest.mark.asyncio
async def test_inactive_or_missing_profile_is_not_exposed() -> None:
    repository = SocialProfileRepositoryStub()
    repository.available = False
    service = SocialProfileService(repository)

    with pytest.raises(ProfileNotFoundError):
        await service.get_profile(repository.profile_id, uuid4())


@pytest.mark.asyncio
async def test_profile_search_normalizes_the_live_query() -> None:
    repository = SocialProfileRepositoryStub()
    service = SocialProfileService(repository)

    results = await service.search_profiles("  Mohammad   Qawasmi ", 8)

    assert repository.search_query == "Mohammad Qawasmi"
    assert results[0].user_id == repository.profile_id
