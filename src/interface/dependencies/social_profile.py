from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.social_profile_service import SocialProfileService
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.repositories.social_profile_repository import (
    SqlAlchemySocialProfileRepository,
)
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.integrations.supabase_avatar_storage import SupabaseAvatarStorage
from src.infrastructure.repositories.profile_avatar_repository import SqlAlchemyProfileAvatarRepository
from src.app.services.profile_avatar_service import ProfileAvatarService


def get_social_profile_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> SocialProfileService:
    storage = SupabaseAvatarStorage(settings.supabase_url, settings.supabase_secret_key, settings.profile_avatars_bucket)
    return SocialProfileService(SqlAlchemySocialProfileRepository(session, storage), ProfileAvatarService(SqlAlchemyProfileAvatarRepository(session), storage))

