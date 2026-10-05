from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.services.social_profile_service import SocialProfileService
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.repositories.social_profile_repository import (
    SqlAlchemySocialProfileRepository,
)


def get_social_profile_service(
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> SocialProfileService:
    return SocialProfileService(SqlAlchemySocialProfileRepository(session))

