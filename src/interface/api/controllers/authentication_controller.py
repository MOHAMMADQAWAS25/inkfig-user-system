from src.app.services.authentication_service import AuthenticationService
from src.entities.dto.authentication import (
    LoginRequest,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
)


class AuthenticationController:
    def __init__(self, service: AuthenticationService) -> None:
        self._service = service

    async def login(self, request: LoginRequest) -> TokenResponse:
        return await self._service.login(request.email, request.password)

    async def refresh(self, request: RefreshTokenRequest) -> TokenResponse:
        return await self._service.refresh(request.refresh_token)

    async def logout(self, request: LogoutRequest) -> None:
        await self._service.logout(request.refresh_token)
