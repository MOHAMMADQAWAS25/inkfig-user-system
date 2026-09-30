from src.app.services.password_reset_service import PasswordResetService
from src.entities.dto.authentication import (
    PasswordResetConfirmRequest, PasswordResetRequest, PasswordResetRequestResponse,
    PasswordResetVerifyRequest, PasswordResetVerifyResponse,
)


class PasswordResetController:
    def __init__(self, service: PasswordResetService) -> None:
        self._service = service

    async def request(self, data: PasswordResetRequest) -> PasswordResetRequestResponse:
        return await self._service.request(data.email)

    async def verify(self, data: PasswordResetVerifyRequest) -> PasswordResetVerifyResponse:
        return await self._service.verify(data.email, data.code)

    async def confirm(self, data: PasswordResetConfirmRequest) -> None:
        await self._service.confirm(data.email, data.reset_token, data.password)
