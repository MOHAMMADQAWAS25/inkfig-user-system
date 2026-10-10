import asyncio
import json
from uuid import UUID

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.config.settings import get_settings
from src.infrastructure.db.postgres.models.user_profile import (
    RolePermissionModel,
    UserAccountModel,
    UserRoleModel,
    WebSocketConnectionModel,
)


async def _publish(
    session: AsyncSession, connection_ids: list[str], event_type: str
) -> None:
    endpoint = get_settings().websocket_management_endpoint
    if not endpoint or not connection_ids:
        return
    client = boto3.client("apigatewaymanagementapi", endpoint_url=endpoint)
    stale: list[str] = []
    payload = json.dumps({"type": event_type}).encode()
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


async def publish_notifications_changed(session: AsyncSession, user_id: UUID) -> None:
    connection_ids = list(
        await session.scalars(
            select(WebSocketConnectionModel.connection_id).where(
                WebSocketConnectionModel.user_id == user_id
            )
        )
    )
    await _publish(session, connection_ids, "notifications.changed")


async def publish_reports_changed(session: AsyncSession) -> None:
    connection_ids = list(
        await session.scalars(
            select(WebSocketConnectionModel.connection_id)
            .join(
                UserRoleModel,
                UserRoleModel.user_id == WebSocketConnectionModel.user_id,
            )
            .join(
                RolePermissionModel,
                and_(
                    RolePermissionModel.role_code == UserRoleModel.role_code,
                    RolePermissionModel.permission_code == "reports.manage",
                ),
            )
            .join(
                UserAccountModel,
                UserAccountModel.user_id == WebSocketConnectionModel.user_id,
            )
            .where(
                UserAccountModel.account_status == "active",
                UserAccountModel.email_verified_at.is_not(None),
            )
            .distinct()
        )
    )
    await _publish(session, connection_ids, "reports.changed")
