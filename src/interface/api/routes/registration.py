from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.entities.dto.registration import RegisterUserRequest, RegisterUserResponse
from src.entities.exceptions.registration import (
    EmailAlreadyRegisteredError,
    RegistrationProviderError,
)
from src.interface.api.controllers.registration_controller import RegistrationController
from src.interface.dependencies.registration import get_registration_controller

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/signup",
    response_model=RegisterUserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    request: RegisterUserRequest,
    controller: Annotated[
        RegistrationController, Depends(get_registration_controller)
    ],
) -> RegisterUserResponse:
    try:
        return await controller.register(request)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from error
    except RegistrationProviderError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Registration is temporarily unavailable.",
        ) from error
