import asyncio
from typing import Any
from uuid import UUID

import jwt
from sqlalchemy import delete

from src.infrastructure.config.settings import get_settings
from src.infrastructure.db.postgres.models.user_profile import WebSocketConnectionModel
from src.infrastructure.db.postgres.session import get_session_factory


async def _handle(event: dict[str, Any]) -> dict[str, int]:
    context = event.get("requestContext", {})
    route = context.get("routeKey")
    connection_id = context.get("connectionId")
    if not connection_id:
        return {"statusCode": 400}
    async with get_session_factory()() as session:
        if route == "$connect":
            ticket = (event.get("queryStringParameters") or {}).get("ticket")
            try:
                if not ticket:
                    raise ValueError("missing ticket")
                settings = get_settings()
                claims = jwt.decode(
                    ticket,
                    settings.jwt_secret,
                    algorithms=["HS256"],
                    issuer=settings.jwt_issuer,
                )
                if claims.get("type") != "websocket":
                    raise ValueError("wrong ticket type")
                user_id = UUID(claims["sub"])
            except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
                return {"statusCode": 401}
            await session.merge(
                WebSocketConnectionModel(connection_id=connection_id, user_id=user_id)
            )
            await session.commit()
        elif route == "$disconnect":
            await session.execute(
                delete(WebSocketConnectionModel).where(
                    WebSocketConnectionModel.connection_id == connection_id
                )
            )
            await session.commit()
    return {"statusCode": 200}


def handler(event: dict[str, Any], context: Any) -> dict[str, int]:
    return asyncio.run(_handle(event))
