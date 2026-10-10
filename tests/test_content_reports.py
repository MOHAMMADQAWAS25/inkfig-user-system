from pathlib import Path

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
