from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.settings import ProfileSettingsResponse, UpdateProfileSettingsRequest
from src.entities.exceptions.settings import PhoneNumberAlreadyExistsError, ProfileNotFoundError
from src.entities.enums.gender import Gender
from src.infrastructure.db.postgres.models.user_profile import RefreshTokenModel, UserAccountModel, UserProfileModel


class SqlAlchemySettingsRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_profile(self, user_id: UUID) -> ProfileSettingsResponse | None:
        row = (await self._session.execute(
            select(UserProfileModel, UserAccountModel.is_active)
            .join(UserAccountModel, UserAccountModel.user_id == UserProfileModel.user_id)
            .where(UserProfileModel.user_id == user_id)
        )).first()
        return None if row is None else self._to_response(row[0], row[1])

    async def get_password_hash(self, user_id: UUID) -> str | None:
        return (await self._session.execute(
            select(UserAccountModel.password_hash).where(UserAccountModel.user_id == user_id)
        )).scalar_one_or_none()

    async def update_profile(self, user_id: UUID, request: UpdateProfileSettingsRequest) -> ProfileSettingsResponse:
        model = (await self._session.execute(
            select(UserProfileModel).where(UserProfileModel.user_id == user_id).with_for_update()
        )).scalar_one_or_none()
        if model is None:
            raise ProfileNotFoundError
        model.full_name = request.full_name
        model.phone_number = request.phone_number
        model.gender = request.gender.value
        model.date_of_birth = request.date_of_birth
        try:
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            original = error.orig
            cause = getattr(original, "__cause__", None)
            constraint = getattr(original, "constraint_name", None) or getattr(cause, "constraint_name", None)
            if constraint == "user_profiles_phone_number_unique_idx":
                raise PhoneNumberAlreadyExistsError from error
            raise
        return (await self.get_profile(user_id))  # type: ignore[return-value]

    async def update_password(self, user_id: UUID, password_hash: str) -> None:
        await self._session.execute(
            update(UserAccountModel).where(UserAccountModel.user_id == user_id)
            .values(password_hash=password_hash, token_version=UserAccountModel.token_version + 1)
        )
        await self._invalidate_refresh_tokens(user_id)

    async def set_active(self, user_id: UUID, is_active: bool) -> None:
        await self._session.execute(
            update(UserAccountModel).where(UserAccountModel.user_id == user_id)
            .values(is_active=is_active, token_version=UserAccountModel.token_version + 1)
        )
        await self._session.execute(
            update(UserProfileModel).where(UserProfileModel.user_id == user_id).values(is_active=is_active)
        )
        await self._invalidate_refresh_tokens(user_id)

    async def _invalidate_refresh_tokens(self, user_id: UUID) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == user_id, RefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self._session.commit()

    @staticmethod
    def _to_response(profile: UserProfileModel, is_active: bool) -> ProfileSettingsResponse:
        return ProfileSettingsResponse(
            email=profile.email, full_name=profile.full_name, phone_number=profile.phone_number,
            gender=Gender(profile.gender), date_of_birth=profile.date_of_birth, is_active=is_active,
        )
