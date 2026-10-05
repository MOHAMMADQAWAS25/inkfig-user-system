from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.authentication import PasswordResetChallenge
from src.infrastructure.db.postgres.models.user_profile import (
    PasswordResetCodeModel,
    RefreshTokenModel,
    UserAccountModel,
)


class SqlAlchemyPasswordResetRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_challenge(
        self, user_id: UUID, code_hash: str, expires_at: datetime, max_attempts: int
    ) -> None:
        now = datetime.now(expires_at.tzinfo)
        await self._session.execute(
            update(PasswordResetCodeModel)
            .where(
                PasswordResetCodeModel.user_id == user_id,
                PasswordResetCodeModel.consumed_at.is_(None),
                PasswordResetCodeModel.invalidated_at.is_(None),
            )
            .values(invalidated_at=now)
        )
        self._session.add(
            PasswordResetCodeModel(
                challenge_id=uuid4(), user_id=user_id, code_hash=code_hash,
                expires_at=expires_at, max_attempts=max_attempts,
            )
        )
        await self._session.commit()

    async def get_pending(self, email: str) -> PasswordResetChallenge | None:
        statement = (
            select(PasswordResetCodeModel, UserAccountModel.email)
            .join(UserAccountModel, UserAccountModel.user_id == PasswordResetCodeModel.user_id)
            .where(
                UserAccountModel.email == email,
                PasswordResetCodeModel.consumed_at.is_(None),
                PasswordResetCodeModel.invalidated_at.is_(None),
                PasswordResetCodeModel.verified_at.is_(None),
            )
            .order_by(PasswordResetCodeModel.sent_at.desc()).limit(1).with_for_update()
        )
        row = (await self._session.execute(statement)).first()
        if row is None:
            return None
        challenge, account_email = row
        return PasswordResetChallenge(
            challenge_id=challenge.challenge_id, user_id=challenge.user_id,
            email=account_email, code_hash=challenge.code_hash,
            expires_at=challenge.expires_at, attempts=challenge.attempts,
            max_attempts=challenge.max_attempts,
        )

    async def record_failed_attempt(self, challenge_id: UUID) -> None:
        await self._session.execute(
            update(PasswordResetCodeModel)
            .where(PasswordResetCodeModel.challenge_id == challenge_id)
            .values(attempts=PasswordResetCodeModel.attempts + 1)
        )
        await self._session.commit()

    async def verify_challenge(
        self, challenge_id: UUID, token_hash: str, token_expires_at: datetime, verified_at: datetime
    ) -> None:
        await self._session.execute(
            update(PasswordResetCodeModel)
            .where(PasswordResetCodeModel.challenge_id == challenge_id)
            .values(verified_at=verified_at, reset_token_hash=token_hash,
                    reset_token_expires_at=token_expires_at)
        )
        await self._session.commit()

    async def reset_password(
        self, email: str, token_hash: str, password_hash: str, now: datetime
    ) -> bool:
        statement = (
            select(PasswordResetCodeModel, UserAccountModel)
            .join(UserAccountModel, UserAccountModel.user_id == PasswordResetCodeModel.user_id)
            .where(
                UserAccountModel.email == email,
                UserAccountModel.account_status != "admin_suspended",
                UserAccountModel.email_verified_at.is_not(None),
                PasswordResetCodeModel.reset_token_hash == token_hash,
                PasswordResetCodeModel.verified_at.is_not(None),
                PasswordResetCodeModel.reset_token_expires_at > now,
                PasswordResetCodeModel.consumed_at.is_(None),
                PasswordResetCodeModel.invalidated_at.is_(None),
            ).with_for_update()
        )
        row = (await self._session.execute(statement)).first()
        if row is None:
            await self._session.rollback()
            return False
        challenge, account = row
        account.password_hash = password_hash
        account.token_version += 1
        account.updated_at = now
        challenge.consumed_at = now
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.user_id == account.user_id,
                   RefreshTokenModel.revoked_at.is_(None))
            .values(revoked_at=now)
        )
        await self._session.commit()
        return True
