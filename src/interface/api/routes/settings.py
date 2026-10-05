from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.app.services.settings_service import SettingsService
from src.entities.dto.settings import AccountStatusRequest, ChangePasswordRequest, ProfileSettingsResponse, UpdateProfileSettingsRequest
from src.entities.exceptions.settings import CurrentPasswordInvalidError, PhoneNumberAlreadyExistsError, ProfileNotFoundError
from src.interface.dependencies.authorization import Principal, require_permission
from src.interface.dependencies.settings import get_settings_service
from src.interface.security.auth_cookies import clear_auth_cookies
from src.infrastructure.config.settings import Settings, get_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/profile", response_model=ProfileSettingsResponse)
async def get_profile(
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SettingsService, Depends(get_settings_service)],
) -> ProfileSettingsResponse:
    try:
        return await service.get_profile(principal.user_id)
    except ProfileNotFoundError as error:
        raise HTTPException(404, "Profile not found.") from error


@router.put("/profile", response_model=ProfileSettingsResponse)
async def update_profile(
    request: UpdateProfileSettingsRequest,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SettingsService, Depends(get_settings_service)],
) -> ProfileSettingsResponse:
    try:
        return await service.update_profile(principal.user_id, request)
    except PhoneNumberAlreadyExistsError as error:
        raise HTTPException(409, "An account with this phone number already exists.") from error
    except ProfileNotFoundError as error:
        raise HTTPException(404, "Profile not found.") from error


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    request: ChangePasswordRequest,
    response: Response,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SettingsService, Depends(get_settings_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    try:
        await service.change_password(principal.user_id, request)
    except CurrentPasswordInvalidError as error:
        raise HTTPException(400, "The current password is incorrect.") from error
    clear_auth_cookies(response, settings)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.put("/account-status", status_code=status.HTTP_204_NO_CONTENT)
async def set_account_status(
    request: AccountStatusRequest,
    response: Response,
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    service: Annotated[SettingsService, Depends(get_settings_service)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    try:
        await service.deactivate(principal.user_id, request.current_password)
    except CurrentPasswordInvalidError as error:
        raise HTTPException(400, "The current password is incorrect.") from error
    clear_auth_cookies(response, settings)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
