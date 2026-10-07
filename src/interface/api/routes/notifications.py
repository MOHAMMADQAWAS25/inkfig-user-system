from datetime import datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.interface.dependencies.authorization import Principal, require_permission

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationItem(BaseModel):
    notification_id: UUID
    event_type: str
    actor_user_id: UUID
    actor_name: str
    actor_avatar_url: str | None
    work_id: UUID | None
    created_at: datetime
    read: bool


class NotificationFeed(BaseModel):
    items: list[NotificationItem]
    unread_count: int


@router.get("", response_model=NotificationFeed)
async def list_notifications(
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    session: Annotated[AsyncSession, Depends(get_database_session)],
    settings: Annotated[Settings, Depends(get_settings)],
    limit: int = Query(50, ge=1, le=100),
) -> NotificationFeed:
    rows = (await session.execute(text("""
        select n.notification_id, n.event_type, n.actor_user_id,
               coalesce(p.full_name, 'InkFig artist') actor_name,
               p.avatar_object_path, n.work_id, n.created_at, n.read_at
        from notifications n
        left join user_profiles p on p.user_id = n.actor_user_id
        where n.recipient_user_id = :recipient
        order by n.created_at desc, n.notification_id desc limit :limit
    """), {"recipient": principal.user_id, "limit": limit})).mappings()
    unread = await session.scalar(text("select count(*) from notifications where recipient_user_id=:recipient and read_at is null"), {"recipient": principal.user_id})
    base = settings.supabase_url.rstrip("/")
    bucket = settings.profile_avatars_bucket
    return NotificationFeed(items=[NotificationItem(
        notification_id=row.notification_id, event_type=row.event_type,
        actor_user_id=row.actor_user_id, actor_name=row.actor_name,
        actor_avatar_url=f"{base}/storage/v1/object/public/{bucket}/{row.avatar_object_path}" if row.avatar_object_path else None,
        work_id=row.work_id, created_at=row.created_at, read=row.read_at is not None,
    ) for row in rows], unread_count=int(unread or 0))


@router.put("/read", status_code=204)
async def mark_notifications_read(
    principal: Annotated[Principal, Depends(require_permission("profile.read_own"))],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> Response:
    await session.execute(text("update notifications set read_at=now() where recipient_user_id=:recipient and read_at is null"), {"recipient": principal.user_id})
    await session.commit()
    return Response(status_code=204)
