from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.postgres.models.user_profile import UserAccountModel
from src.infrastructure.repositories.authentication_repository import SqlAlchemyAuthenticationRepository


@pytest.mark.asyncio
@pytest.mark.parametrize("previous_session", [None, uuid4()])
async def test_first_login_is_claimed_under_account_lock_with_session_in_same_commit(previous_session: object) -> None:
    db = AsyncMock(spec=AsyncSession)
    user_id = uuid4()
    account = UserAccountModel(user_id=user_id, email="12345678@students.hebron.edu", first_login_at=None, backup_email=None)
    db.scalar.side_effect = [account, previous_session]
    repository = SqlAlchemyAuthenticationRepository(cast(AsyncSession, db))
    show = await repository.store_refresh_token(uuid4(), user_id, "hash", datetime.now(timezone.utc) + timedelta(days=30), record_login=True)
    assert show is (previous_session is None)
    assert "FOR UPDATE" in str(db.scalar.call_args_list[0].args[0])
    assert account.first_login_at is not None
    db.add.assert_called_once()
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_already_recorded_login_does_not_claim_prompt_again() -> None:
    db = AsyncMock(spec=AsyncSession)
    db.scalar.return_value = UserAccountModel(first_login_at=datetime.now(timezone.utc))
    repository = SqlAlchemyAuthenticationRepository(cast(AsyncSession, db))
    assert not await repository.store_refresh_token(uuid4(), uuid4(), "hash", datetime.now(timezone.utc), record_login=True)
    db.scalar.assert_awaited_once()


def test_migration_backfills_all_prior_sessions_without_expiry_or_revocation_filter() -> None:
    sql = (Path(__file__).parents[1] / "migrations/20261018_022_track_first_login.sql").read_text(encoding="utf-8")
    assert "first_login_at timestamptz null" in sql
    assert "min(created_at)" in sql
    assert "expires_at" not in sql
    assert "revoked_at" not in sql
    assert "delete" not in sql.lower()
