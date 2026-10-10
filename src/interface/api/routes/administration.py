from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.services.administration_service import AdministrationDeniedError, AdministrationService, ManagedUserNotFoundError
from src.entities.dto.administration import ChangeRoleRequest, ChangeStatusRequest, UserAdministrationPage, UserAdministrationResponse
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.repositories.administration_repository import SqlAlchemyAdministrationRepository
from src.interface.dependencies.authorization import Principal, require_permission

router = APIRouter(prefix="/admin/users", tags=["administration"])

def service(session: Annotated[AsyncSession, Depends(get_database_session)]) -> AdministrationService:
    return AdministrationService(SqlAlchemyAdministrationRepository(session))

@router.get("", response_model=UserAdministrationPage)
async def list_users(app: Annotated[AdministrationService, Depends(service)], _: Annotated[Principal, Depends(require_permission("users.read"))], limit: int = Query(50, ge=1, le=100), cursor: int = Query(0, ge=0, le=100_000)) -> UserAdministrationPage:
    items, next_cursor = await app.list_users(limit, cursor)
    return UserAdministrationPage(items=items, next_cursor=next_cursor)

@router.patch("/{user_id}/role", response_model=UserAdministrationResponse)
async def change_role(user_id: UUID, request: ChangeRoleRequest, app: Annotated[AdministrationService, Depends(service)], actor: Annotated[Principal, Depends(require_permission("users.role.manage"))]) -> UserAdministrationResponse:
    try: return await app.change_role(actor.user_id, actor.role, user_id, request.role)
    except ManagedUserNotFoundError as error: raise HTTPException(404, "User not found.") from error
    except AdministrationDeniedError as error: raise HTTPException(403, "You cannot assign or manage this role.") from error

@router.patch("/{user_id}/status", response_model=UserAdministrationResponse)
async def change_status(user_id: UUID, request: ChangeStatusRequest, app: Annotated[AdministrationService, Depends(service)], actor: Annotated[Principal, Depends(require_permission("users.status.manage"))]) -> UserAdministrationResponse:
    try: return await app.change_status(actor.user_id, actor.role, user_id, request.is_active)
    except ManagedUserNotFoundError as error: raise HTTPException(404, "User not found.") from error
    except AdministrationDeniedError as error: raise HTTPException(403, "You cannot manage this account.") from error
