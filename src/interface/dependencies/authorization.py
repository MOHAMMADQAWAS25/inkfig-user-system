from dataclasses import dataclass
from collections.abc import Callable, Coroutine
from typing import Annotated, Any
from uuid import UUID
import jwt
from fastapi import Cookie, Depends, HTTPException
from src.entities.enums.role import Role
from src.infrastructure.config.settings import Settings, get_settings


@dataclass(frozen=True)
class Principal:
    user_id: UUID
    role: Role
    permissions: frozenset[str]


def require_permission(permission: str) -> Callable[..., Coroutine[Any, Any, Principal]]:
    async def dependency(settings: Annotated[Settings, Depends(get_settings)], access_token: Annotated[str | None, Cookie(alias="inkfig_access")] = None) -> Principal:
        if not access_token: raise HTTPException(401, "Authentication is required.")
        try:
            claims = jwt.decode(access_token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer)
            principal = Principal(UUID(claims["sub"]), Role(claims["role"]), frozenset(claims.get("permissions", [])))
        except Exception as error: raise HTTPException(401, "Invalid or expired access token.") from error
        if permission not in principal.permissions and "system.manage" not in principal.permissions: raise HTTPException(403, "You do not have permission to perform this action.")
        return principal
    return dependency
