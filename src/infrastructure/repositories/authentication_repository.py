from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.authentication import AuthenticatedUser
from src.entities.enums.account_status import AccountStatus
from src.infrastructure.db.postgres.models.user_profile import (
    RefreshTokenModel,
    RolePermissionModel,
    UserAccountModel,
    UserProfileModel,
    UserRoleModel,
)


class SqlAlchemyAuthenticationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_user_by_email(self, email: str) -> AuthenticatedUser | None:
        statement = (
            select(UserAccountModel, UserProfileModel.full_name, UserRoleModel.role_code)
            .join(UserProfileModel, UserProfileModel.user_id == UserAccountModel.user_id)
            .join(UserRoleModel, UserRoleModel.user_id == UserAccountModel.user_id)
            .where(UserAccountModel.email == email)
        )
        row = (await self._session.execute(statement)).first()
        if row is None:
            return None
        permissions = list((await self._session.execute(select(RolePermissionModel.permission_code).where(RolePermissionModel.role_code == row[2]))).scalars())
        return self._to_user(row[0], row[1], row[2], permissions)

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

    async def reactivate_self_deactivated(self, user_id: UUID) -> AuthenticatedUser:
        await self._session.execute(update(UserAccountModel).where(UserAccountModel.user_id == user_id, UserAccountModel.account_status == AccountStatus.SELF_DEACTIVATED.value).values(is_active=True, account_status=AccountStatus.ACTIVE.value, token_version=UserAccountModel.token_version + 1))
        await self._session.execute(update(UserProfileModel).where(UserProfileModel.user_id == user_id).values(is_active=True))
        await self._session.commit()
        result = await self.find_user_by_email((await self._session.scalar(select(UserAccountModel.email).where(UserAccountModel.user_id == user_id))) or "")
        assert result is not None
        return result

    async def consume_refresh_token(
        self, token_hash: str, consumed_at: datetime
    ) -> AuthenticatedUser | None:
        statement = (
            select(RefreshTokenModel, UserAccountModel, UserProfileModel.full_name, UserRoleModel.role_code)
            .join(UserAccountModel, UserAccountModel.user_id == RefreshTokenModel.user_id)
            .join(UserProfileModel, UserProfileModel.user_id == UserAccountModel.user_id)
            .join(UserRoleModel, UserRoleModel.user_id == UserAccountModel.user_id)
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
        token, account, full_name, role = row
        token.revoked_at = consumed_at
        await self._session.commit()
        permissions = list((await self._session.execute(select(RolePermissionModel.permission_code).where(RolePermissionModel.role_code == role))).scalars())
        return self._to_user(account, full_name, role, permissions)

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
    def _to_user(account: UserAccountModel, full_name: str, role: str, permissions: list[str]) -> AuthenticatedUser:
        return AuthenticatedUser(
            user_id=account.user_id,
            email=account.email,
            full_name=full_name,
            password_hash=account.password_hash,
            is_active=account.is_active,
            account_status=AccountStatus(account.account_status),
            email_verified_at=account.email_verified_at,
            token_version=account.token_version,
            role=role,
            permissions=permissions,
        )
