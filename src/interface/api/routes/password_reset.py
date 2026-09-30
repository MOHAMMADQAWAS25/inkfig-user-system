from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from src.entities.dto.authentication import (
    PasswordResetConfirmRequest,
    PasswordResetRequest,
    PasswordResetRequestResponse,
    PasswordResetVerifyRequest,
    PasswordResetVerifyResponse,
)
from src.entities.exceptions.authentication import (
    PasswordResetAttemptsExceededError,
    PasswordResetCodeExpiredError,
    PasswordResetCodeInvalidError,
    PasswordResetTokenInvalidError,
)
from src.entities.exceptions.registration import EmailDeliveryError
from src.interface.api.controllers.password_reset_controller import PasswordResetController
from src.interface.dependencies.password_reset import get_password_reset_controller

router = APIRouter(prefix="/auth/password-reset", tags=["authentication"])


@router.post(
    "/request",
    response_model=PasswordResetRequestResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def request_password_reset(
    request: PasswordResetRequest,
    controller: Annotated[PasswordResetController, Depends(get_password_reset_controller)],
) -> PasswordResetRequestResponse:
    try:
        return await controller.request(request)
    except EmailDeliveryError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The reset email could not be sent.",
        ) from error


@router.post("/verify", response_model=PasswordResetVerifyResponse)
async def verify_password_reset(
    request: PasswordResetVerifyRequest,
    controller: Annotated[PasswordResetController, Depends(get_password_reset_controller)],
) -> PasswordResetVerifyResponse:
    try:
        return await controller.verify(request)
    except PasswordResetCodeExpiredError as error:
        raise HTTPException(status_code=410, detail="The reset code has expired.") from error
    except PasswordResetAttemptsExceededError as error:
        raise HTTPException(status_code=429, detail="Too many incorrect reset attempts.") from error
    except PasswordResetCodeInvalidError as error:
        raise HTTPException(status_code=400, detail="The reset code is incorrect.") from error


@router.post("/confirm", status_code=status.HTTP_204_NO_CONTENT)
async def confirm_password_reset(
    request: PasswordResetConfirmRequest,
    controller: Annotated[PasswordResetController, Depends(get_password_reset_controller)],
) -> Response:
    try:
        await controller.confirm(request)
    except PasswordResetTokenInvalidError as error:
        raise HTTPException(
            status_code=400,
            detail="The password-reset session is invalid or expired.",
        ) from error
    return Response(status_code=status.HTTP_204_NO_CONTENT)
