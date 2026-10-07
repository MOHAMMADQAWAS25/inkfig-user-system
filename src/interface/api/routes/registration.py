from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.entities.dto.registration import (
    RegisterUserRequest,
    RegisterUserResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)
from src.entities.exceptions.email_code_rate_limit import (
    EmailCodeRateLimitExceededError,
)
from src.entities.exceptions.registration import (
    EmailAlreadyRegisteredError,
    EmailDeliveryError,
    PhoneAlreadyRegisteredError,
    RegistrationProviderError,
    VerificationAttemptsExceededError,
    VerificationCodeExpiredError,
    VerificationCodeInvalidError,
    VerificationNotFoundError,
    VerificationResendTooSoonError,
)
from src.interface.api.controllers.registration_controller import RegistrationController
from src.interface.dependencies.registration import get_registration_controller
from src.entities.exceptions.profile_avatar import AvatarStorageError, AvatarUploadNotFoundError, UnsupportedAvatarError

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
    except PhoneAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this phone number already exists.",
        ) from error
    except EmailCodeRateLimitExceededError as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Five verification codes were requested. Try again in one hour.",
            headers={"Retry-After": str(error.retry_after_seconds)},
        ) from error
    except EmailDeliveryError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The verification email could not be sent.",
        ) from error
    except UnsupportedAvatarError as error:
        raise HTTPException(status_code=422, detail="Choose a JPEG, PNG, or WebP image up to 2 MB.") from error
    except AvatarStorageError as error:
        raise HTTPException(status_code=503, detail="Avatar storage is temporarily unavailable.") from error


@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    request: VerifyEmailRequest,
    controller: Annotated[RegistrationController, Depends(get_registration_controller)],
) -> VerifyEmailResponse:
    try:
        return await controller.verify_email(request)
    except VerificationCodeInvalidError as error:
        raise HTTPException(status_code=400, detail="The verification code is incorrect.") from error
    except VerificationCodeExpiredError as error:
        raise HTTPException(status_code=410, detail="The verification code has expired.") from error
    except VerificationAttemptsExceededError as error:
        raise HTTPException(status_code=429, detail="Too many incorrect verification attempts.") from error
    except VerificationNotFoundError as error:
        raise HTTPException(status_code=404, detail="No pending verification was found.") from error
    except RegistrationProviderError as error:
        raise HTTPException(status_code=503, detail="Verification is temporarily unavailable.") from error
    except AvatarUploadNotFoundError as error:
        raise HTTPException(status_code=400, detail="The selected profile picture was not uploaded.") from error
    except AvatarStorageError as error:
        raise HTTPException(status_code=503, detail="Avatar storage is temporarily unavailable.") from error


@router.post("/resend-verification", response_model=ResendVerificationResponse)
async def resend_verification(
    request: ResendVerificationRequest,
    controller: Annotated[RegistrationController, Depends(get_registration_controller)],
) -> ResendVerificationResponse:
    try:
        return await controller.resend_verification(request)
    except VerificationResendTooSoonError as error:
        raise HTTPException(status_code=429, detail="Wait before requesting another code.") from error
    except EmailCodeRateLimitExceededError as error:
        raise HTTPException(
            status_code=429,
            detail="Five verification codes were requested. Try again in one hour.",
            headers={"Retry-After": str(error.retry_after_seconds)},
        ) from error
    except VerificationNotFoundError as error:
        raise HTTPException(status_code=404, detail="No pending verification was found.") from error
    except EmailDeliveryError as error:
        raise HTTPException(status_code=503, detail="The verification email could not be sent.") from error
