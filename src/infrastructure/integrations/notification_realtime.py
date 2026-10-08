import asyncio
import json
from uuid import UUID

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.config.settings import get_settings
from src.infrastructure.db.postgres.models.user_profile import WebSocketConnectionModel


async def publish_notifications_changed(session: AsyncSession, user_id: UUID) -> None:
    endpoint = get_settings().websocket_management_endpoint
    if not endpoint:
        return
    connection_ids = list(
        await session.scalars(
            select(WebSocketConnectionModel.connection_id).where(
                WebSocketConnectionModel.user_id == user_id
            )
        )
    )
    if not connection_ids:
        return
    client = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)
    stale: list[str] = []
    payload = json.dumps({"type": "notifications.changed"}).encode()
    for connection_id in connection_ids:
        try:
            await asyncio.to_thread(
                client.post_to_connection, ConnectionId=connection_id, Data=payload
            )
        except ClientError as error:
            if error.response.get("ResponseMetadata", {}).get("HTTPStatusCode") == 410:
                stale.append(connection_id)
    if stale:
        await session.execute(
            delete(WebSocketConnectionModel).where(
                WebSocketConnectionModel.connection_id.in_(stale)
            )
        )
        await session.commit()
