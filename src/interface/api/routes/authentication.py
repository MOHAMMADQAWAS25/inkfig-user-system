from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.entities.dto.authentication import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)
from src.entities.exceptions.authentication import (
    AccountInactiveError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from src.interface.api.controllers.authentication_controller import AuthenticationController
from src.interface.dependencies.authentication import get_authentication_controller

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> TokenResponse:
    try:
        return await controller.login(request)
    except InvalidCredentialsError as error:
        raise HTTPException(status_code=401, detail="Invalid email or password.") from error
    except AccountInactiveError as error:
        raise HTTPException(status_code=403, detail="Verify your email before signing in.") from error


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: RefreshTokenRequest,
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> TokenResponse:
    try:
        return await controller.refresh(request)
    except (InvalidRefreshTokenError, AccountInactiveError) as error:
        raise HTTPException(status_code=401, detail="The refresh token is invalid.") from error


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest,
    controller: Annotated[AuthenticationController, Depends(get_authentication_controller)],
) -> Response:
    await controller.logout(request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
