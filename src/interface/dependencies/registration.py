from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.registration_service import RegistrationService
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.integrations.supabase_auth import SupabaseAuthGateway
from src.infrastructure.integrations.brevo_email import BrevoVerificationEmailGateway
from src.infrastructure.repositories.user_profile_repository import (
    SqlAlchemyUserProfileRepository,
)
from src.interface.api.controllers.registration_controller import RegistrationController


def get_auth_gateway(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SupabaseAuthGateway:
    return SupabaseAuthGateway(settings.supabase_url, settings.supabase_secret_key)


def get_registration_service(
    auth_gateway: Annotated[SupabaseAuthGateway, Depends(get_auth_gateway)],
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> RegistrationService:
    return RegistrationService(
        auth_gateway=auth_gateway,
        profile_repository=SqlAlchemyUserProfileRepository(session),
        email_gateway=BrevoVerificationEmailGateway(
            settings.brevo_api_key,
            settings.brevo_sender_email,
            settings.brevo_sender_name,
            settings.brevo_verify_email_template_id,
        ),
        hash_secret=settings.supabase_secret_key,
        code_ttl_minutes=settings.verification_code_ttl_minutes,
        max_attempts=settings.verification_max_attempts,
        resend_cooldown_seconds=settings.verification_resend_cooldown_seconds,
    )


def get_registration_controller(
    service: Annotated[RegistrationService, Depends(get_registration_service)],
) -> RegistrationController:
    return RegistrationController(service)
