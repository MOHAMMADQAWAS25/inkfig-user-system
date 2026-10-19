from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.interface.api.routes.notifications import unread_count
from src.interface.dependencies.authorization import Principal


@pytest.mark.asyncio
async def test_unread_summary_never_loads_notification_rows() -> None:
    session = AsyncMock(spec=AsyncSession)
    session.scalar.return_value = 7
    principal = MagicMock(user_id=uuid4())
    result = await unread_count(cast(Principal, principal), cast(AsyncSession, session))
    assert result.unread_count == 7
    sql = str(session.scalar.call_args.args[0])
    assert "count(*)" in sql and "recipient_user_id=:recipient" in sql
    session.execute.assert_not_awaited()


def test_exhibition_notification_migration_preserves_social_upserts_and_history() -> None:
    sql = (Path(__file__).parents[1] / "migrations/20261019_023_exhibition_notifications.sql").read_text()
    assert "notifications_event_unique" in sql
    assert "unique nulls not distinct" in sql
    assert "submission_approved" in sql and "withdrawal_rejected" in sql
    assert "on delete set null" in sql
    assert "delete from" not in sql.lower()
