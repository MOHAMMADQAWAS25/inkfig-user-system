from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.password_reset_service import PasswordResetService
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.integrations.brevo_email import BrevoVerificationEmailGateway
from src.infrastructure.repositories.authentication_repository import SqlAlchemyAuthenticationRepository
from src.infrastructure.repositories.password_reset_repository import SqlAlchemyPasswordResetRepository
from src.infrastructure.security.passwords import Pbkdf2PasswordHasher
from src.interface.api.controllers.password_reset_controller import PasswordResetController


def get_password_reset_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> PasswordResetService:
    email_gateway = BrevoVerificationEmailGateway(
        settings.brevo_api_key, settings.brevo_sender_email,
        settings.brevo_sender_name, settings.brevo_verify_email_template_id,
    )
    return PasswordResetService(
        SqlAlchemyAuthenticationRepository(session),
        SqlAlchemyPasswordResetRepository(session), email_gateway,
        Pbkdf2PasswordHasher(), settings.jwt_secret,
        settings.password_reset_code_ttl_minutes,
        settings.password_reset_max_attempts,
        settings.password_reset_token_ttl_minutes,
    )


def get_password_reset_controller(
    service: Annotated[PasswordResetService, Depends(get_password_reset_service)],
) -> PasswordResetController:
    return PasswordResetController(service)
