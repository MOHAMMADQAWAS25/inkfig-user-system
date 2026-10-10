from uuid import UUID
from src.entities.dto.administration import UserAdministrationResponse
from src.entities.enums.role import ROLE_RANK, Role
from src.entities.repositories.administration import AdministrationRepository


class AdministrationDeniedError(Exception): pass
class ManagedUserNotFoundError(Exception): pass


class AdministrationService:
    def __init__(self, repository: AdministrationRepository) -> None:
        self._repository = repository

    async def list_users(self, limit: int, cursor: int) -> tuple[list[UserAdministrationResponse], int | None]:
        users = await self._repository.list_users(limit + 1, cursor)
        return users[:limit], cursor + limit if len(users) > limit else None

    async def change_role(self, actor_id: UUID, actor_role: Role, target_id: UUID, role: Role) -> UserAdministrationResponse:
        target = await self._required_target(target_id)
        self._assert_can_manage(actor_id, actor_role, target, role)
        await self._repository.set_role(target_id, role, actor_id)
        return (await self._repository.get_user(target_id))  # type: ignore[return-value]

    async def change_status(self, actor_id: UUID, actor_role: Role, target_id: UUID, is_active: bool) -> UserAdministrationResponse:
        target = await self._required_target(target_id)
        self._assert_can_manage(actor_id, actor_role, target)
        await self._repository.set_active(target_id, is_active)
        return (await self._repository.get_user(target_id))  # type: ignore[return-value]

    async def _required_target(self, user_id: UUID) -> UserAdministrationResponse:
        target = await self._repository.get_user(user_id)
        if target is None: raise ManagedUserNotFoundError
        return target

    @staticmethod
    def _assert_can_manage(actor_id: UUID, actor_role: Role, target: UserAdministrationResponse, new_role: Role | None = None) -> None:
        if actor_role not in (Role.ADMIN, Role.SYSTEM_ADMINISTRATOR) or actor_id == target.user_id:
            raise AdministrationDeniedError
        if actor_role != Role.SYSTEM_ADMINISTRATOR:
            if ROLE_RANK[target.role] >= ROLE_RANK[actor_role]: raise AdministrationDeniedError
            if new_role is not None and ROLE_RANK[new_role] >= ROLE_RANK[actor_role]: raise AdministrationDeniedError
