from pathlib import Path
from typing import Literal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from src.interface.api.routes.reports import CreateReportRequest

ROOT = Path(__file__).resolve().parents[1]
ROUTE = (ROOT / "src/interface/api/routes/reports.py").read_text(encoding="utf-8")
MIGRATION = (ROOT / "migrations/20261010_018_create_content_reports.sql").read_text(encoding="utf-8")


def test_report_endpoints_are_permission_gated_and_paginated() -> None:
    assert 'require_permission("reports.create")' in ROUTE
    assert 'require_permission("reports.manage")' in ROUTE
    assert "limit: int = Query(25, ge=1, le=100)" in ROUTE
    assert "next_cursor" in ROUTE
    assert "You cannot report yourself or your own work" in ROUTE
    assert "returning report_id" in ROUTE
    assert "scalar_one_or_none()" in ROUTE
    assert ".rowcount" not in ROUTE
    assert "cast(:status as text) is null" in ROUTE


def test_report_schema_keeps_an_auditable_moderation_queue() -> None:
    assert "create table public.content_reports" in MIGRATION
    assert "reviewer_user_id" in MIGRATION
    assert "reviewed_at" in MIGRATION
    assert "content_reports_unique_user_report_idx" in MIGRATION
    assert "content_reports_unique_work_report_idx" in MIGRATION
    assert "('admin', 'reports.manage')" in MIGRATION
    assert "enable row level security" in MIGRATION


@pytest.mark.parametrize("target", ["user", "work"])
@pytest.mark.parametrize("details", [None, "", "   \n  ", "short", "a     b"])
def test_other_requires_meaningful_details(target: Literal["user", "work"], details: str | None) -> None:
    with pytest.raises(ValidationError):
        CreateReportRequest(target_type=target, target_user_id=uuid4(),
                            target_work_id=uuid4() if target == "work" else None,
                            reason_code="other", details=details)


@pytest.mark.parametrize("target", ["user", "work"])
def test_other_accepts_normalized_details_and_preserves_limits(target: Literal["user", "work"]) -> None:
    report = CreateReportRequest(target_type=target, target_user_id=uuid4(),
                                 target_work_id=uuid4() if target == "work" else None,
                                 reason_code="other", details="  Please   check\nthis account  ")
    assert report.details == "Please check this account"
    assert len(CreateReportRequest.model_validate({**report.model_dump(), "details": "x" * 2000}).details or "") == 2000
    with pytest.raises(ValidationError):
        CreateReportRequest.model_validate({**report.model_dump(), "details": "x" * 2001})


@pytest.mark.parametrize("reason", ["impersonation", "harassment", "spam", "hate_speech"])
def test_user_reasons_allow_optional_details(reason: str) -> None:
    report = CreateReportRequest.model_validate({"target_type": "user", "target_user_id": uuid4(), "reason_code": reason})
    assert report.details is None


@pytest.mark.parametrize("reason", ["sexual_content", "violence", "copyright"])
def test_user_rejects_removed_or_post_only_reasons(reason: str) -> None:
    with pytest.raises(ValidationError):
        CreateReportRequest.model_validate({"target_type": "user", "target_user_id": uuid4(), "reason_code": reason})


def test_post_rejects_removed_reason_but_keeps_post_only_reasons() -> None:
    payload = {"target_type": "work", "target_user_id": uuid4(), "target_work_id": uuid4(), "reason_code": "sexual_content"}
    with pytest.raises(ValidationError):
        CreateReportRequest.model_validate(payload)
    for reason in ("violence", "copyright"):
        assert CreateReportRequest.model_validate({**payload, "reason_code": reason}).details is None
