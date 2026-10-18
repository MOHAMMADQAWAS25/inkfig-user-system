from pathlib import Path
from datetime import datetime, timedelta, timezone
from typing import cast
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.postgres.models.user_profile import UserAccountModel
from src.infrastructure.repositories.password_reset_repository import SqlAlchemyPasswordResetRepository


def test_backup_email_is_private_and_changes_invalidate_reset_challenges() -> None:
    root = Path(__file__).parents[1]
    migration = (root / "migrations/20261018_021_add_backup_email.sql").read_text(encoding="utf-8")
    assert "alter table public.user_accounts" in migration
    assert "backup_email varchar(254) null" in migration
    assert "grant" not in migration.split("--")[0].lower()
    repository = (root / "src/infrastructure/repositories/settings_repository.py").read_text(encoding="utf-8")
    assert "PasswordResetCodeModel.user_id == user_id" in repository
    assert ".values(invalidated_at=now)" in repository
    assert ".with_for_update()" in repository
    reset = (root / "src/infrastructure/repositories/password_reset_repository.py").read_text(encoding="utf-8")
    assert "account.backup_email != expected_backup_email" in reset
    assert 'UserAccountModel.account_status != "admin_suspended"' in reset
    routes = (root / "src/interface/api/routes/settings.py").read_text(encoding="utf-8")
    assert 'require_permission("profile.read_own")' in routes
    assert "service.update_backup_email(principal.user_id, request)" in routes


@pytest.mark.asyncio
async def test_changed_backup_aborts_challenge_creation_under_account_lock() -> None:
    db = AsyncMock(spec=AsyncSession)
    db.scalar.return_value = UserAccountModel(
        user_id=uuid4(), email="12345678@students.hebron.edu", backup_email=None,
        email_verified_at=datetime.now(timezone.utc), account_status="active",
    )
    repository = SqlAlchemyPasswordResetRepository(cast(AsyncSession, db))
    created = await repository.create_challenge(uuid4(), "hash", datetime.now(timezone.utc) + timedelta(minutes=10), 5, expected_backup_email="old@gmail.com")
    assert created is False
    assert "FOR UPDATE" in str(db.scalar.call_args.args[0])
    db.execute.assert_not_awaited()
    db.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_unchanged_backup_allows_serialized_challenge_creation() -> None:
    db = AsyncMock(spec=AsyncSession)
    account_id = uuid4()
    db.scalar.return_value = UserAccountModel(
        user_id=account_id, email="12345678@students.hebron.edu", backup_email="student@gmail.com",
        email_verified_at=datetime.now(timezone.utc), account_status="active",
    )
    repository = SqlAlchemyPasswordResetRepository(cast(AsyncSession, db))
    assert await repository.create_challenge(account_id, "hash", datetime.now(timezone.utc) + timedelta(minutes=10), 5, expected_backup_email="student@gmail.com")
    assert "invalidated_at" in str(db.execute.call_args.args[0])
    db.add.assert_called_once()
    db.commit.assert_awaited_once()
