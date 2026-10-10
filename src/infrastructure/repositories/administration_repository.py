from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import select, update
from sqlalchemy.sql import Select
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from src.entities.dto.administration import UserAdministrationResponse
from src.entities.enums.role import Role
from src.entities.enums.account_status import AccountStatus
from src.infrastructure.db.postgres.models.user_profile import RefreshTokenModel, UserAccountModel, UserProfileModel, UserRoleModel


class SqlAlchemyAdministrationRepository:
    def __init__(self, session: AsyncSession) -> None: self._session = session

    def _statement(self) -> Select[Any]:
        return select(UserAccountModel, UserProfileModel.full_name, UserRoleModel.role_code).join(UserProfileModel, UserProfileModel.user_id == UserAccountModel.user_id).join(UserRoleModel, UserRoleModel.user_id == UserAccountModel.user_id)

    async def list_users(self, limit: int, offset: int) -> list[UserAdministrationResponse]:
        rows = (await self._session.execute(self._statement().order_by(UserAccountModel.created_at.desc(), UserAccountModel.user_id).limit(limit).offset(offset))).all()
        return [self._to_response(*row) for row in rows]

    async def get_user(self, user_id: UUID) -> UserAdministrationResponse | None:
        row = (await self._session.execute(self._statement().where(UserAccountModel.user_id == user_id))).first()
        return None if row is None else self._to_response(*row)

    async def set_role(self, user_id: UUID, role: Role, actor_id: UUID) -> None:
        await self._session.execute(update(UserRoleModel).where(UserRoleModel.user_id == user_id).values(role_code=role.value, assigned_by=actor_id, assigned_at=datetime.now(timezone.utc)))
        await self._invalidate_sessions(user_id)

    async def set_active(self, user_id: UUID, is_active: bool) -> None:
        await self._session.execute(update(UserAccountModel).where(UserAccountModel.user_id == user_id).values(is_active=is_active, account_status=AccountStatus.ACTIVE.value if is_active else AccountStatus.ADMIN_SUSPENDED.value, token_version=UserAccountModel.token_version + 1))
        await self._session.execute(update(UserProfileModel).where(UserProfileModel.user_id == user_id).values(is_active=is_active))
        await self._invalidate_sessions(user_id, increment_version=False)

    async def _invalidate_sessions(self, user_id: UUID, increment_version: bool = True) -> None:
        now = datetime.now(timezone.utc)
        if increment_version:
            await self._session.execute(update(UserAccountModel).where(UserAccountModel.user_id == user_id).values(token_version=UserAccountModel.token_version + 1))
        await self._session.execute(update(RefreshTokenModel).where(RefreshTokenModel.user_id == user_id, RefreshTokenModel.revoked_at.is_(None)).values(revoked_at=now))
        await self._session.commit()

    @staticmethod
    def _to_response(account: UserAccountModel, full_name: str, role: str) -> UserAdministrationResponse:
        return UserAdministrationResponse(user_id=account.user_id, email=account.email, full_name=full_name, role=Role(role), is_active=account.is_active)
