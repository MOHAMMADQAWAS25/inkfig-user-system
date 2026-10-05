from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response

from src.app.services.social_profile_service import SocialProfileService
from src.entities.dto.social_profile import (
    ProfileAccountListResponse,
    PublicProfileResponse,
)
from src.entities.exceptions.social_profile import (
    CannotFollowSelfError,
    ProfileNotFoundError,
)
from src.interface.dependencies.authorization import Principal, require_permission
from src.interface.dependencies.social_profile import get_social_profile_service

router = APIRouter(prefix="/profiles", tags=["social profiles"])


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

