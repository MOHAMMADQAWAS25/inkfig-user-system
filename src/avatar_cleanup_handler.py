import asyncio
from typing import Any

from src.app.services.avatar_cleanup_service import AvatarCleanupService
from src.infrastructure.config.settings import get_settings
from src.infrastructure.db.postgres.session import get_session_factory
from src.infrastructure.integrations.supabase_avatar_storage import (
    SupabaseAvatarStorage,
)
from src.infrastructure.repositories.avatar_cleanup_repository import (
    SqlAlchemyAvatarCleanupRepository,
)


async def _handle() -> dict[str, int]:
    settings = get_settings()
    storage = SupabaseAvatarStorage(
        settings.supabase_url,
        settings.supabase_secret_key,
        settings.profile_avatars_bucket,
    )
    async with get_session_factory()() as session:
        result = await AvatarCleanupService(
            SqlAlchemyAvatarCleanupRepository(session), storage
        ).run()
    return {
        "processed": result.processed,
        "deleted": result.deleted,
        "deferred": result.deferred,
    }


def handler(event: dict[str, Any], context: Any) -> dict[str, int]:
    return asyncio.run(_handle())
