from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status

from src.entities.dto.authentication import (
    LoginRequest,
    SessionResponse,
)
from src.entities.exceptions.authentication import (
    AccountInactiveError,
    AccountAdminSuspendedError,
    InvalidCredentialsError,
    InvalidRefreshTokenError,
)
from src.infrastructure.config.settings import Settings, get_settings
from src.interface.api.controllers.authentication_controller import (
    AuthenticationController,
)
from src.interface.dependencies.authentication import get_authentication_controller
from src.interface.security.auth_cookies import (
    clear_auth_cookies,
    session_response,
    set_auth_cookies,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=SessionResponse)
async def login(
    request: LoginRequest,
    response: Response,
    controller: Annotated[
        AuthenticationController, Depends(get_authentication_controller)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SessionResponse:
    try:
        tokens = await controller.login(request)
        set_auth_cookies(response, tokens, settings)
        return session_response(tokens)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=401, detail="Invalid email or password."
        ) from error
    except AccountAdminSuspendedError as error:
        raise HTTPException(status_code=423, detail="This account was suspended by an administrator.") from error
    except AccountInactiveError as error:
        raise HTTPException(
            status_code=403, detail="Verify your email before signing in."
        ) from error


@router.post("/refresh", response_model=SessionResponse)
async def refresh(
    response: Response,
    controller: Annotated[
        AuthenticationController, Depends(get_authentication_controller)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
    refresh_token: Annotated[str | None, Cookie(alias="inkfig_refresh")] = None,
) -> SessionResponse:
    try:
        if not refresh_token:
            raise InvalidRefreshTokenError
        tokens = await controller.refresh_token(refresh_token)
        set_auth_cookies(response, tokens, settings)
        return session_response(tokens)
    except (InvalidRefreshTokenError, AccountInactiveError) as error:
        raise HTTPException(
            status_code=401, detail="The refresh token is invalid."
        ) from error


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    controller: Annotated[
        AuthenticationController, Depends(get_authentication_controller)
    ],
    settings: Annotated[Settings, Depends(get_settings)],
    refresh_token: Annotated[str | None, Cookie(alias="inkfig_refresh")] = None,
) -> Response:
    if refresh_token:
        await controller.logout_token(refresh_token)
    clear_auth_cookies(response, settings)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response
