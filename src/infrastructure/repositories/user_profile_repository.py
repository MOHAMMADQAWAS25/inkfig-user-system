from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.registration import RegisteredUser, UserProfileCreate
from src.entities.enums.gender import Gender
from src.entities.exceptions.registration import EmailAlreadyRegisteredError
from src.infrastructure.db.postgres.models.user_profile import UserProfileModel


class SqlAlchemyUserProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, profile: UserProfileCreate) -> RegisteredUser:
        model = UserProfileModel(
            user_id=profile.user_id,
            email=profile.email,
            full_name=profile.full_name,
            phone_number=profile.phone_number,
            gender=profile.gender.value,
            date_of_birth=profile.date_of_birth,
        )
        self._session.add(model)
        try:
            await self._session.commit()
            await self._session.refresh(model)
        except IntegrityError as error:
            await self._session.rollback()
            raise EmailAlreadyRegisteredError from error
        return RegisteredUser(
            user_id=model.user_id,
            email=model.email,
            full_name=model.full_name,
            phone_number=model.phone_number,
            gender=Gender(model.gender),
            date_of_birth=model.date_of_birth,
            is_active=model.is_active,
            created_at=model.created_at,
        )
