from src.app.services.registration_service import RegistrationService
from src.entities.dto.registration import RegisterUserRequest, RegisterUserResponse


class RegistrationController:
    def __init__(self, registration_service: RegistrationService) -> None:
        self._registration_service = registration_service

    async def register(self, request: RegisterUserRequest) -> RegisterUserResponse:
        return await self._registration_service.register(request)
