from uuid import UUID

from pydantic import BaseModel


class PublicProfileResponse(BaseModel):
    user_id: UUID
    full_name: str
    follower_count: int
    following_count: int
    like_count: int
    is_following: bool
    is_self: bool


class ProfileAccountSummary(BaseModel):
    user_id: UUID
    full_name: str
    is_following: bool


class ProfileAccountListResponse(BaseModel):
    items: list[ProfileAccountSummary]


class ProfileSearchResult(BaseModel):
    user_id: UUID
    full_name: str


class ProfileSearchResponse(BaseModel):
    items: list[ProfileSearchResult]

