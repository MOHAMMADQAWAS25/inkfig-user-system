from typing import cast
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import jwt
import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.enums.role import Role
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.interface.api.routes import reports
from src.interface.dependencies.authorization import Principal


def principal() -> Principal:
    return Principal(uuid4(), Role.ADMIN, frozenset({"reports.manage", "reports.create"}))


@pytest.mark.asyncio
async def test_pending_count_uses_only_pending_summary_query() -> None:
    session = AsyncMock(spec=AsyncSession)
    session.scalar.return_value = 12
    result = await reports.pending_report_count(principal(), cast(AsyncSession, session))
    assert result.pending_count == 12
    assert "count(*) from content_reports where status='pending'" in str(session.scalar.call_args.args[0])
    session.execute.assert_not_awaited()


@pytest.mark.parametrize("permissions,expected", [(None, 401), ([], 403), (["reports.manage"], 200)])
def test_count_endpoint_requires_report_management(permissions: list[str] | None, expected: int) -> None:
    app = FastAPI()
    app.include_router(reports.router, prefix="/api/v1")
    settings = Settings(jwt_secret="test-only-report-counter-signing-key")
    session = AsyncMock(spec=AsyncSession)
    session.scalar.return_value = 3
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_database_session] = lambda: session
    with TestClient(app) as client:
        if permissions is not None:
            token = jwt.encode({"sub": str(uuid4()), "role": "admin", "permissions": permissions, "iss": settings.jwt_issuer}, settings.jwt_secret, algorithm="HS256")
            client.cookies.set("inkfig_access", token)
        response = client.get("/api/v1/reports/pending-count")
    assert response.status_code == expected
    if expected == 200:
        assert response.json() == {"pending_count": 3}
    else:
        session.scalar.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("target", ["user", "work"])
async def test_blocked_reporter_cannot_submit_either_report_type(target: str) -> None:
    session = AsyncMock(spec=AsyncSession)
    session.scalar.return_value = True
    request = reports.CreateReportRequest.model_validate({"target_type": target, "target_user_id": uuid4(), "target_work_id": uuid4() if target == "work" else None, "reason_code": "spam"})
    with pytest.raises(HTTPException) as error:
        await reports.create_report(request, principal(), cast(AsyncSession, session))
    assert error.value.status_code == 403
    assert "for update" in str(session.scalar.call_args.args[0])
    session.execute.assert_not_awaited()
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("delivery_fails", [False, True])
async def test_review_commits_before_live_event_and_survives_delivery_failure(monkeypatch: pytest.MonkeyPatch, delivery_fails: bool) -> None:
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.scalar_one_or_none.return_value = uuid4()
    session.execute.return_value = result
    async def deliver(_: AsyncSession) -> None:
        session.commit.assert_awaited_once()
        if delivery_fails:
            raise RuntimeError("offline")
    publish = AsyncMock(side_effect=deliver)
    monkeypatch.setattr(reports, "publish_reports_changed", publish)
    response = await reports.review_report(uuid4(), reports.ReviewReportRequest(status="dismissed"), principal(), cast(AsyncSession, session))
    assert response.status_code == 204
    publish.assert_awaited_once()
    assert session.rollback.await_count == int(delivery_fails)


@pytest.mark.asyncio
async def test_missing_report_never_commits_or_sends_event(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute.return_value = result
    publish = AsyncMock()
    monkeypatch.setattr(reports, "publish_reports_changed", publish)
    with pytest.raises(HTTPException) as error:
        await reports.review_report(uuid4(), reports.ReviewReportRequest(status="reviewed"), principal(), cast(AsyncSession, session))
    assert error.value.status_code == 404
    session.commit.assert_not_awaited()
    publish.assert_not_awaited()


@pytest.mark.asyncio
async def test_allowed_creation_event_follows_commit(monkeypatch: pytest.MonkeyPatch) -> None:
    session = AsyncMock(spec=AsyncSession)
    session.scalar.side_effect = [False, True]
    async def deliver(_: AsyncSession) -> None:
        session.commit.assert_awaited_once()
    publish = AsyncMock(side_effect=deliver)
    monkeypatch.setattr(reports, "publish_reports_changed", publish)
    request = reports.CreateReportRequest(target_type="user", target_user_id=uuid4(), reason_code="spam")
    response = await reports.create_report(request, principal(), cast(AsyncSession, session))
    assert response.status_code == 204
    publish.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("blocked", [False, True])
async def test_eligibility_is_owner_scoped(blocked: bool) -> None:
    session = AsyncMock(spec=AsyncSession)
    session.scalar.return_value = blocked
    actor = principal()
    result = await reports.reporting_eligibility(actor, cast(AsyncSession, session))
    assert result.allowed is not blocked
    assert session.scalar.call_args.args[1] == {"user_id": actor.user_id}


@pytest.mark.asyncio
@pytest.mark.parametrize("blocked", [False, True])
async def test_admin_can_block_and_restore_reporter_without_deleting_reports(monkeypatch: pytest.MonkeyPatch, blocked: bool) -> None:
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value.first.return_value = {"user_id": uuid4(), "role_code": "user"}
    session.execute.return_value = result
    publish = AsyncMock()
    monkeypatch.setattr(reports, "publish_reports_changed", publish)
    actor = principal()
    target = uuid4()
    response = await reports.restrict_reporter(target, reports.ReportingRestriction(blocked=blocked), actor, cast(AsyncSession, session))
    assert response.status_code == 204
    sql, parameters = session.execute.call_args.args
    assert "reporting_blocked=:blocked" in str(sql)
    assert "reporting_restriction_updated_by=:actor" in str(sql)
    assert "delete" not in str(sql).lower()
    assert parameters == {"blocked": blocked, "actor": actor.user_id, "user_id": target}
    session.commit.assert_awaited_once()
    publish.assert_awaited_once()


@pytest.mark.asyncio
@pytest.mark.parametrize("role", ["admin", "system_administrator"])
async def test_admin_reporting_cannot_be_blocked(role: str) -> None:
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value.first.return_value = {"user_id": uuid4(), "role_code": role}
    session.execute.return_value = result
    with pytest.raises(HTTPException) as error:
        await reports.restrict_reporter(uuid4(), reports.ReportingRestriction(blocked=True), principal(), cast(AsyncSession, session))
    assert error.value.status_code == 403
    session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_duplicate_report_still_returns_conflict(monkeypatch: pytest.MonkeyPatch) -> None:
    from sqlalchemy.exc import IntegrityError
    session = AsyncMock(spec=AsyncSession)
    session.scalar.side_effect = [False, True]
    session.execute.side_effect = IntegrityError("insert", {}, Exception("duplicate"))
    publish = AsyncMock()
    monkeypatch.setattr(reports, "publish_reports_changed", publish)
    with pytest.raises(HTTPException) as error:
        await reports.create_report(reports.CreateReportRequest(target_type="user", target_user_id=uuid4(), reason_code="spam"), principal(), cast(AsyncSession, session))
    assert error.value.status_code == 409
    session.rollback.assert_awaited_once()
    session.commit.assert_not_awaited()
    publish.assert_not_awaited()


@pytest.mark.parametrize("endpoint,permission", [("eligibility", "reports.create"), ("restriction", "reports.manage")])
@pytest.mark.parametrize("authorized", [False, True])
def test_reporting_restriction_and_eligibility_endpoints_enforce_permissions(endpoint: str, permission: str, authorized: bool) -> None:
    app = FastAPI()
    app.include_router(reports.router, prefix="/api/v1")
    settings = Settings(jwt_secret="test-only-report-restriction-signing-key")
    session = AsyncMock(spec=AsyncSession)
    session.scalar.return_value = False
    result = MagicMock()
    result.mappings.return_value.first.return_value = {"role_code": "user"}
    session.execute.return_value = result
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_database_session] = lambda: session
    token = jwt.encode({"sub": str(uuid4()), "role": "admin", "permissions": [permission] if authorized else [], "iss": settings.jwt_issuer}, settings.jwt_secret, algorithm="HS256")
    with TestClient(app) as client:
        client.cookies.set("inkfig_access", token)
        if endpoint == "eligibility":
            response = client.get("/api/v1/reports/eligibility")
        else:
            response = client.put(f"/api/v1/reports/reporters/{uuid4()}/restriction", json={"blocked": True})
    assert response.status_code == ((200 if endpoint == "eligibility" else 204) if authorized else 403)
    if not authorized:
        session.scalar.assert_not_awaited()
        session.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_self_restriction_is_rejected_without_query() -> None:
    session = AsyncMock(spec=AsyncSession)
    actor = principal()
    with pytest.raises(HTTPException) as error:
        await reports.restrict_reporter(actor.user_id, reports.ReportingRestriction(blocked=True), actor, cast(AsyncSession, session))
    assert error.value.status_code == 403
    session.execute.assert_not_awaited()


@pytest.mark.asyncio
async def test_missing_reporter_is_not_updated() -> None:
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.mappings.return_value.first.return_value = None
    session.execute.return_value = result
    with pytest.raises(HTTPException) as error:
        await reports.restrict_reporter(uuid4(), reports.ReportingRestriction(blocked=True), principal(), cast(AsyncSession, session))
    assert error.value.status_code == 404
    session.commit.assert_not_awaited()
