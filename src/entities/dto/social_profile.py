from uuid import UUID

from pydantic import BaseModel


class PublicProfileResponse(BaseModel):
    user_id: UUID
    full_name: str
    avatar_url: str | None = None
    follower_count: int
    following_count: int
    like_count: int
    is_following: bool
    is_self: bool


class ProfileAccountSummary(BaseModel):
    user_id: UUID
    full_name: str
    avatar_url: str | None = None
    is_following: bool


class ProfileAccountListResponse(BaseModel):
    items: list[ProfileAccountSummary]
    next_cursor: int | None = None


class ProfileSearchResult(BaseModel):
    user_id: UUID
    full_name: str
    avatar_url: str | None = None


class ProfileSearchResponse(BaseModel):
    items: list[ProfileSearchResult]
    next_cursor: int | None = None

