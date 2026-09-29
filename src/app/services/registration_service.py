from src.entities.dto.registration import (
    RegisterUserRequest,
    RegisterUserResponse,
    UserProfileCreate,
)
from src.entities.repositories.registration import AuthUserGateway, UserProfileRepository


class RegistrationService:
    def __init__(
        self,
        auth_gateway: AuthUserGateway,
        profile_repository: UserProfileRepository,
    ) -> None:
        self._auth_gateway = auth_gateway
        self._profile_repository = profile_repository

    async def register(self, request: RegisterUserRequest) -> RegisterUserResponse:
        user_id = await self._auth_gateway.create_user(request.email, request.password)
        try:
            user = await self._profile_repository.create(
                UserProfileCreate(
                    user_id=user_id,
                    email=request.email,
                    full_name=request.full_name,
                    phone_number=request.phone_number,
                    gender=request.gender,
                    date_of_birth=request.date_of_birth,
                )
            )
        except Exception:
            await self._auth_gateway.delete_user(user_id)
            raise
        return RegisterUserResponse(user=user)
