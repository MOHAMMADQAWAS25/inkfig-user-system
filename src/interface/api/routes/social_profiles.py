from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from src.app.services.social_profile_service import SocialProfileService
from src.entities.dto.profile_avatar import (
    AvatarResponse,
    AvatarUploadRequest,
    AvatarUploadResponse,
    CompleteAvatarUploadRequest,
)
from src.entities.dto.social_profile import (
    ProfileAccountListResponse,
    ProfileSearchResponse,
    PublicProfileResponse,
)
from src.entities.exceptions.profile_avatar import (
    AvatarStorageError,
    AvatarUploadNotFoundError,
    UnsupportedAvatarError,
)
from src.entities.exceptions.social_profile import (
    CannotFollowSelfError,
    ProfileNotFoundError,
)
from src.interface.dependencies.authorization import Principal, require_permission
from src.interface.dependencies.social_profile import get_social_profile_service

router = APIRouter(prefix="/profiles", tags=["social profiles"])


@router.get("/search", response_model=ProfileSearchResponse)
async def search_profiles(
    service: Annotated[SocialProfileService, Depends(get_social_profile_service)],
    query: str = Query(min_length=1, max_length=120),
    limit: int = Query(8, ge=1, le=20),
    cursor: int = Query(0, ge=0, le=10_000),
) -> ProfileSearchResponse:
    items, next_cursor = await service.search_profiles(query, limit, cursor)
    return ProfileSearchResponse(items=items, next_cursor=next_cursor)
@router.post("/avatar-uploads", response_model=AvatarUploadResponse, status_code=201)
async def prepare_avatar_upload(
    request: AvatarUploadRequest,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SocialProfileService, Depends(get_social_profile_service)],
) -> AvatarUploadResponse:
    try:
        return await service.prepare_avatar_upload(principal.user_id, request)
    except UnsupportedAvatarError as error:
        raise HTTPException(422, "Choose a JPEG, PNG, or WebP image up to 2 MB.") from error
    except AvatarStorageError as error:
        raise HTTPException(503, "Avatar storage is temporarily unavailable.") from error


@router.post("/avatar-uploads/complete", response_model=AvatarResponse)
async def complete_avatar_upload(
    request: CompleteAvatarUploadRequest,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SocialProfileService, Depends(get_social_profile_service)],
) -> AvatarResponse:
    try:
        return await service.complete_avatar_upload(principal.user_id, request.object_path)
    except AvatarUploadNotFoundError as error:
        raise HTTPException(404, "The uploaded avatar was not found.") from error
    except AvatarStorageError as error:
        raise HTTPException(503, "Avatar storage is temporarily unavailable.") from error


@router.get("/{user_id}", response_model=PublicProfileResponse)
async def get_profile(
    user_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SocialProfileService, Depends(get_social_profile_service)],
) -> PublicProfileResponse:
    try:
        return await service.get_profile(user_id, principal.user_id)
    except ProfileNotFoundError as error:
        raise HTTPException(404, "Profile not found.") from error


@router.get("/{user_id}/followers", response_model=ProfileAccountListResponse)
async def followers(
    user_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SocialProfileService, Depends(get_social_profile_service)],
) -> ProfileAccountListResponse:
    try:
        return ProfileAccountListResponse(
            items=await service.list_followers(user_id, principal.user_id)
        )
    except ProfileNotFoundError as error:
        raise HTTPException(404, "Profile not found.") from error


@router.get("/{user_id}/following", response_model=ProfileAccountListResponse)
async def following(
    user_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SocialProfileService, Depends(get_social_profile_service)],
) -> ProfileAccountListResponse:
    try:
        return ProfileAccountListResponse(
            items=await service.list_following(user_id, principal.user_id)
        )
    except ProfileNotFoundError as error:
        raise HTTPException(404, "Profile not found.") from error


@router.put("/{user_id}/follow", status_code=204)
async def follow(
    user_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SocialProfileService, Depends(get_social_profile_service)],
) -> Response:
    try:
        await service.set_follow(principal.user_id, user_id, True)
    except CannotFollowSelfError as error:
        raise HTTPException(409, "You cannot follow your own account.") from error
    except ProfileNotFoundError as error:
        raise HTTPException(404, "Profile not found.") from error
    return Response(status_code=204)


@router.delete("/{user_id}/follow", status_code=204)
async def unfollow(
    user_id: UUID,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SocialProfileService, Depends(get_social_profile_service)],
) -> Response:
    try:
        await service.set_follow(principal.user_id, user_id, False)
    except CannotFollowSelfError as error:
        raise HTTPException(409, "You cannot unfollow your own account.") from error
    except ProfileNotFoundError as error:
        raise HTTPException(404, "Profile not found.") from error
    return Response(status_code=204)

