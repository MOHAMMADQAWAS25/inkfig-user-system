from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.authentication import AuthenticatedUser
from src.infrastructure.db.postgres.models.user_profile import (
    RefreshTokenModel,
    UserAccountModel,
    UserProfileModel,
)


class SqlAlchemyAuthenticationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_user_by_email(self, email: str) -> AuthenticatedUser | None:
        statement = (
            select(UserAccountModel, UserProfileModel.full_name)
            .join(UserProfileModel, UserProfileModel.user_id == UserAccountModel.user_id)
            .where(UserAccountModel.email == email)
        )
        row = (await self._session.execute(statement)).first()
        return None if row is None else self._to_user(row[0], row[1])

    async def store_refresh_token(
        self, token_id: UUID, user_id: UUID, token_hash: str, expires_at: datetime
    ) -> None:
        self._session.add(
            RefreshTokenModel(
                token_id=token_id,
                user_id=user_id,
                token_hash=token_hash,
                expires_at=expires_at,
            )
        )
        await self._session.commit()

    async def consume_refresh_token(
        self, token_hash: str, consumed_at: datetime
    ) -> AuthenticatedUser | None:
        statement = (
            select(RefreshTokenModel, UserAccountModel, UserProfileModel.full_name)
            .join(UserAccountModel, UserAccountModel.user_id == RefreshTokenModel.user_id)
            .join(UserProfileModel, UserProfileModel.user_id == UserAccountModel.user_id)
            .where(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.revoked_at.is_(None),
                RefreshTokenModel.expires_at > consumed_at,
            )
            .with_for_update()
        )
        row = (await self._session.execute(statement)).first()
        if row is None:
            await self._session.rollback()
            return None
        token, account, full_name = row
        token.revoked_at = consumed_at
        await self._session.commit()
        return self._to_user(account, full_name)

    async def revoke_refresh_token(self, token_hash: str, revoked_at: datetime) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.token_hash == token_hash,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
        )
        await self._session.commit()

    @staticmethod
    def _to_user(account: UserAccountModel, full_name: str) -> AuthenticatedUser:
        return AuthenticatedUser(
            user_id=account.user_id,
            email=account.email,
            full_name=full_name,
            password_hash=account.password_hash,
            is_active=account.is_active,
            email_verified_at=account.email_verified_at,
            token_version=account.token_version,
        )
