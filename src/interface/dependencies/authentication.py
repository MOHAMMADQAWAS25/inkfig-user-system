from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.authentication_service import AuthenticationService
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.repositories.authentication_repository import (
    SqlAlchemyAuthenticationRepository,
)
from src.infrastructure.security.passwords import Pbkdf2PasswordHasher
from src.interface.api.controllers.authentication_controller import AuthenticationController


def get_authentication_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthenticationService:
    return AuthenticationService(
        repository=SqlAlchemyAuthenticationRepository(session),
        password_hasher=Pbkdf2PasswordHasher(),
        jwt_secret=settings.jwt_secret,
        jwt_issuer=settings.jwt_issuer,
        access_token_minutes=settings.access_token_minutes,
        refresh_token_days=settings.refresh_token_days,
    )


def get_authentication_controller(
    service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> AuthenticationController:
    return AuthenticationController(service)
