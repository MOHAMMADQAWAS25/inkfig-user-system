from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.registration import (
    EmailVerificationCreate,
    PendingEmailVerification,
    RegisteredUser,
    UserProfileCreate,
)
from src.entities.enums.gender import Gender
from src.entities.exceptions.registration import EmailAlreadyRegisteredError
from src.infrastructure.db.postgres.models.user_profile import (
    EmailVerificationCodeModel,
    UserProfileModel,
)


class SqlAlchemyUserProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_pending(
        self, profile: UserProfileCreate, verification: EmailVerificationCreate
    ) -> RegisteredUser:
        model = UserProfileModel(
            user_id=profile.user_id,
            email=profile.email,
            full_name=profile.full_name,
            phone_number=profile.phone_number,
            gender=profile.gender.value,
            date_of_birth=profile.date_of_birth,
            is_active=False,
        )
        code_model = EmailVerificationCodeModel(
            verification_id=uuid4(),
            user_id=verification.user_id,
            code_hash=verification.code_hash,
            expires_at=verification.expires_at,
            max_attempts=verification.max_attempts,
        )
        self._session.add_all([model, code_model])
        try:
            await self._session.commit()
            await self._session.refresh(model)
        except IntegrityError as error:
            await self._session.rollback()
            raise EmailAlreadyRegisteredError from error
        return self._to_registered_user(model)

    async def get_pending_verification(
        self, email: str
    ) -> PendingEmailVerification | None:
        statement = (
            select(EmailVerificationCodeModel, UserProfileModel)
            .join(UserProfileModel, UserProfileModel.user_id == EmailVerificationCodeModel.user_id)
            .where(
                UserProfileModel.email == email,
                UserProfileModel.is_active.is_(False),
                EmailVerificationCodeModel.consumed_at.is_(None),
                EmailVerificationCodeModel.invalidated_at.is_(None),
            )
            .order_by(EmailVerificationCodeModel.sent_at.desc())
            .limit(1)
            .with_for_update()
        )
        row = (await self._session.execute(statement)).first()
        if row is None:
            return None
        code, profile = row
        return PendingEmailVerification(
            verification_id=code.verification_id,
            user_id=code.user_id,
            email=profile.email,
            full_name=profile.full_name,
            code_hash=code.code_hash,
            expires_at=code.expires_at,
            attempts=code.attempts,
            max_attempts=code.max_attempts,
            sent_at=code.sent_at,
        )

    async def record_failed_attempt(self, verification_id: UUID) -> None:
        await self._session.execute(
            update(EmailVerificationCodeModel)
            .where(EmailVerificationCodeModel.verification_id == verification_id)
            .values(attempts=EmailVerificationCodeModel.attempts + 1)
        )
        await self._session.commit()

    async def activate_verified_user(
        self, verification_id: UUID, user_id: UUID, verified_at: datetime
    ) -> None:
        await self._session.execute(
            update(EmailVerificationCodeModel)
            .where(EmailVerificationCodeModel.verification_id == verification_id)
            .values(consumed_at=verified_at)
        )
        await self._session.execute(
            update(UserProfileModel)
            .where(UserProfileModel.user_id == user_id)
            .values(is_active=True, email_verified_at=verified_at, updated_at=verified_at)
        )
        await self._session.commit()

    async def replace_verification(
        self, previous_id: UUID, verification: EmailVerificationCreate
    ) -> None:
        now = datetime.now(verification.expires_at.tzinfo)
        await self._session.execute(
            update(EmailVerificationCodeModel)
            .where(EmailVerificationCodeModel.verification_id == previous_id)
            .values(invalidated_at=now)
        )
        self._session.add(
            EmailVerificationCodeModel(
                verification_id=uuid4(),
                user_id=verification.user_id,
                code_hash=verification.code_hash,
                expires_at=verification.expires_at,
                max_attempts=verification.max_attempts,
            )
        )
        await self._session.commit()

    @staticmethod
    def _to_registered_user(model: UserProfileModel) -> RegisteredUser:
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
