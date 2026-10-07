from src.app.services.registration_service import RegistrationService
from src.entities.dto.registration import (
    RegisterUserRequest,
    RegisterUserResponse,
    ResendVerificationRequest,
    ResendVerificationResponse,
    VerifyEmailRequest,
    VerifyEmailResponse,
)


class RegistrationController:
    def __init__(self, registration_service: RegistrationService) -> None:
        self._registration_service = registration_service

    async def register(self, request: RegisterUserRequest) -> RegisterUserResponse:
        return await self._registration_service.register(request)

    async def verify_email(self, request: VerifyEmailRequest) -> VerifyEmailResponse:
        return await self._registration_service.verify_email(request.email, request.code, request.avatar_object_path)

    async def resend_verification(
        self, request: ResendVerificationRequest
    ) -> ResendVerificationResponse:
        return await self._registration_service.resend_verification(request.email)
