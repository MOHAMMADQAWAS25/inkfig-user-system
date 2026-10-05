from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.settings_service import SettingsService
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.repositories.settings_repository import SqlAlchemySettingsRepository
from src.infrastructure.security.passwords import Pbkdf2PasswordHasher


def get_settings_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> SettingsService:
    return SettingsService(SqlAlchemySettingsRepository(session), Pbkdf2PasswordHasher())
