from datetime import date, datetime, timezone
from typing import Any, Literal, cast
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import jwt
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Table, create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from src.app.services.administration_service import AdministrationService
from src.entities.enums.role import Role
from src.infrastructure.config.settings import Settings, get_settings
from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.db.postgres.models.user_profile import UserAccountModel, UserProfileModel, UserRoleModel
from src.infrastructure.repositories.administration_repository import SqlAlchemyAdministrationRepository
from src.interface.api.routes import administration, reports
from src.interface.dependencies.authorization import Principal


class SessionAdapter:
    def __init__(self, session: Session) -> None:
        self.session = session

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        return self.session.execute(*args, **kwargs)

    async def scalar(self, *args: Any, **kwargs: Any) -> Any:
        return self.session.scalar(*args, **kwargs)


@pytest.mark.asyncio
async def test_user_filters_counts_and_pagination_execute_before_limit() -> None:
    engine = create_engine("sqlite://")
    try:
        for model in [UserAccountModel, UserProfileModel, UserRoleModel]:
            cast(Table, model.__table__).create(engine)
        with Session(engine) as session:
            for index in range(33):
                # Keep alphabetic digits: SQLite's UUID affinity must not coerce IDs to integers.
                user_id = UUID(f"abcdef00-0000-0000-0000-{index + 1:012x}")
                session.add(UserAccountModel(user_id=user_id, email=f"artist{index}@example.com", password_hash="test-only", is_active=index >= 15, created_at=datetime(2026, 10, 1, tzinfo=timezone.utc)))
                session.add(UserProfileModel(user_id=user_id, email=f"artist{index}@example.com", full_name="Special 50%_ Artist" if index == 32 else "Ordinary Artist", phone_number=f"059{index:07d}", gender="female", date_of_birth=date(2000, 1, 1)))
                session.add(UserRoleModel(user_id=user_id, role_code="admin" if index == 32 else "user"))
            session.flush()
            repository = SqlAlchemyAdministrationRepository(cast(AsyncSession, SessionAdapter(session)))
            service = AdministrationService(repository)
            first = await service.list_users(10, 0, "artist", Role.USER, True)
            second = await service.list_users(10, 10, "artist", Role.USER, True)
            assert first.total == second.total == 17
            assert len(first.items) == 10 and len(second.items) == 7
            assert first.next_cursor == 10 and second.next_cursor is None
            assert not {user.user_id for user in first.items} & {user.user_id for user in second.items}
            assert first.summary.total == 33 and first.summary.active == 18 and first.summary.administrators == 1
            special = await service.list_users(10, 0, "  SPECIAL 50%_  ", Role.ADMIN, True)
            assert special.total == 1 and len(special.items) == 1
            literal = await service.list_users(10, 0, "%_", None, None)
            assert literal.total == 1 and literal.items[0].user_id == UUID("abcdef00-0000-0000-0000-000000000021")
            absent = await service.list_users(10, 0, "no such name", None, None)
            assert absent.total == 0 and absent.items == []
            assert (await service.list_users(10, 0, "", Role.USER, False)).total == 15
    finally:
        engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("sort", ["newest", "oldest"])
async def test_report_filters_are_applied_before_limit_with_global_scoped_counts(sort: Literal["newest", "oldest"]) -> None:
    engine = create_engine("sqlite://")
    try:
        with Session(engine) as session:
            for sql in [
                "create table content_reports (report_id text,reporter_user_id text,target_type text,target_user_id text,target_work_id text,reason_code text,details text,status text,reviewer_notes text,created_at text,reviewed_at text)",
                "create table user_profiles (user_id text,full_name text)",
                "create table user_accounts (user_id text,reporting_blocked boolean)",
                "create table user_roles (user_id text,role_code text)",
                "create table works (work_id text,title text)",
            ]:
                session.execute(text(sql))
            ids = []
            for index in range(42):
                report_id = str(uuid4()); ids.append(report_id)
                session.execute(text("insert into content_reports values (:id,:actor,:type,:target,null,:reason,null,:status,null,:created,null)"),
                                {"id": report_id, "actor": str(uuid4()), "type": "work" if index >= 30 else "user", "target": str(uuid4()), "reason": "copyright" if index >= 30 else "spam", "status": "reviewed" if index == 41 else "pending", "created": f"2026-10-{index % 28 + 1:02d}T00:00:00Z"})
            principal = Principal(uuid4(), Role.ADMIN, frozenset({"reports.manage"}))
            adapter = cast(AsyncSession, SessionAdapter(session))
            if sort == "newest":
                unfiltered = await reports.list_reports(principal, adapter, "pending", 5, 0, None, None, sort)
                assert all(row.reason_code == "spam" for row in unfiltered.items)
            page = await reports.list_reports(principal, adapter, "pending", 5, 0, "work", "copyright", sort)
            continuation = await reports.list_reports(principal, adapter, "pending", 5, 5, "work", "copyright", sort)
            assert len(page.items) == len(continuation.items) == 5
            assert page.total == 11 and page.type_counts == {"all": 11, "work": 11, "user": 0}
            assert page.next_cursor == 5 and continuation.next_cursor == 10
            combined = page.items + continuation.items
            assert all(row.reason_code == "copyright" and row.target_type == "work" and row.status == "pending" for row in combined)
            assert len({row.report_id for row in combined}) == 10
            positions = [(row.created_at, str(row.report_id)) for row in combined]
            assert positions == sorted(positions, reverse=sort == "newest")
            empty = await reports.list_reports(principal, adapter, "pending", 5, 100, "work", "copyright", sort)
            assert empty.items == [] and empty.total == 11 and empty.next_cursor is None
    finally:
        engine.dispose()


@pytest.mark.parametrize("path,permission", [("/reports", "reports.manage"), ("/admin/users", "users.read")])
@pytest.mark.parametrize("granted,status", [(None, 401), (False, 403), (True, 200)])
def test_list_permissions_and_new_query_validation(path: str, permission: str, granted: bool | None, status: int) -> None:
    app = FastAPI(); app.include_router(reports.router); app.include_router(administration.router)
    settings = Settings(jwt_secret="server-filtered-pagination-test-key")
    app.dependency_overrides[get_settings] = lambda: settings
    session = AsyncMock(spec=AsyncSession)
    session.execute.return_value.mappings = lambda: type("Rows", (), {"one": lambda self: {"all_count": 0, "work_count": 0, "user_count": 0}, "all": lambda self: []})()
    app.dependency_overrides[get_database_session] = lambda: session
    service = AsyncMock()
    service.list_users.return_value = {"items": [], "total": 0, "next_cursor": None}
    app.dependency_overrides[administration.service] = lambda: service
    with TestClient(app) as client:
        if granted is not None:
            token = jwt.encode({"sub": str(uuid4()), "role": "admin", "permissions": [permission] if granted else [], "iss": settings.jwt_issuer}, settings.jwt_secret, algorithm="HS256")
            client.cookies.set("inkfig_access", token)
        response = client.get(path)
        assert response.status_code == status
        if granted:
            invalid = "?target_type=invalid&sort=invalid&reason_code=invalid" if path == "/reports" else "?role=invalid&is_active=invalid"
            assert client.get(path + invalid).status_code == 422
