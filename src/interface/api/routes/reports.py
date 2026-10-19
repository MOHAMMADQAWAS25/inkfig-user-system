import logging
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.postgres.session import get_database_session
from src.infrastructure.integrations.notification_realtime import (
    publish_reports_changed,
)
from src.interface.dependencies.authorization import Principal, require_permission

router = APIRouter(prefix="/reports", tags=["reports"])
ReasonCode = Literal["harassment", "hate_speech", "violence", "spam", "copyright", "impersonation", "other"]
ReportStatus = Literal["pending", "reviewed", "dismissed", "actioned"]


class CreateReportRequest(BaseModel):
    target_type: Literal["work", "user"]
    target_user_id: UUID
    target_work_id: UUID | None = None
    reason_code: ReasonCode
    details: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def validate_target_and_details(self) -> "CreateReportRequest":
        if (self.target_type == "work") != (self.target_work_id is not None):
            raise ValueError("A work report requires a work identifier.")
        if self.target_type == "user" and self.reason_code not in {
            "impersonation", "harassment", "spam", "hate_speech", "other"
        }:
            raise ValueError("This reason is only available for work reports.")
        if self.details is not None:
            self.details = " ".join(self.details.split()) or None
            if self.details is not None and len(self.details) < 10:
                raise ValueError("Report details must contain at least 10 characters.")
        if self.reason_code == "other" and self.details is None:
            raise ValueError("Additional details are required for Other reports.")
        return self


class ReviewReportRequest(BaseModel):
    status: Literal["reviewed", "dismissed", "actioned"]
    notes: str | None = Field(default=None, max_length=2000)


class ReportItem(BaseModel):
    report_id: UUID
    reporter_user_id: UUID
    reporter_name: str
    reporter_reporting_blocked: bool = False
    reporter_can_be_restricted: bool = False
    target_type: str
    target_user_id: UUID
    target_user_name: str
    target_work_id: UUID | None
    target_work_title: str | None
    reason_code: str
    details: str | None
    status: str
    reviewer_notes: str | None
    created_at: datetime
    reviewed_at: datetime | None


class ReportPage(BaseModel):
    items: list[ReportItem]
    next_cursor: int | None = None


class PendingReportCount(BaseModel):
    pending_count: int


class ReportingEligibility(BaseModel):
    allowed: bool


class ReportingRestriction(BaseModel):
    blocked: bool


@router.get("/eligibility", response_model=ReportingEligibility)
async def reporting_eligibility(
    principal: Annotated[Principal, Depends(require_permission("reports.create"))],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> ReportingEligibility:
    blocked = await session.scalar(text("select reporting_blocked from user_accounts where user_id=:user_id"), {"user_id": principal.user_id})
    if blocked is None:
        raise HTTPException(404, "Account not found.")
    return ReportingEligibility(allowed=not blocked)


@router.put("/reporters/{user_id}/restriction", status_code=204)
async def restrict_reporter(
    user_id: UUID,
    request: ReportingRestriction,
    principal: Annotated[Principal, Depends(require_permission("reports.manage"))],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> Response:
    if user_id == principal.user_id:
        raise HTTPException(403, "You cannot restrict your own reporting access.")
    row = (await session.execute(text("""
        select ua.user_id, ur.role_code from user_accounts ua
        left join user_roles ur on ur.user_id=ua.user_id
        where ua.user_id=:user_id for update of ua
    """), {"user_id": user_id})).mappings().first()
    if row is None:
        raise HTTPException(404, "Account not found.")
    if row["role_code"] in {"admin", "system_administrator"}:
        raise HTTPException(403, "Administrator reporting access cannot be restricted here.")
    await session.execute(text("""
        update user_accounts set reporting_blocked=:blocked,
        reporting_restriction_updated_by=:actor, reporting_restriction_updated_at=now(), updated_at=now()
        where user_id=:user_id
    """), {"blocked": request.blocked, "actor": principal.user_id, "user_id": user_id})
    await session.commit()
    await notify_report_managers(session)
    return Response(status_code=204)


@router.get("/pending-count", response_model=PendingReportCount)
async def pending_report_count(
    _: Annotated[Principal, Depends(require_permission("reports.manage"))],
    session: Annotated[AsyncSession, Depends(get_database_session)],
) -> PendingReportCount:
    count = await session.scalar(text("select count(*) from content_reports where status='pending'"))
    return PendingReportCount(pending_count=int(count or 0))


async def notify_report_managers(session: AsyncSession) -> None:
    """The report mutation is already committed; delivery must not undo it."""
    try:
        await publish_reports_changed(session)
    except Exception:
        await session.rollback()
        logging.getLogger(__name__).exception("Report live delivery failed; report state remains saved")


@router.post("", status_code=204)
async def create_report(request: CreateReportRequest, principal: Annotated[Principal, Depends(require_permission("reports.create"))], session: Annotated[AsyncSession, Depends(get_database_session)]) -> Response:
    # Serialize against admin restrictions so an already-blocked user cannot race a submission.
    blocked = await session.scalar(text("select reporting_blocked from user_accounts where user_id=:user_id for update"), {"user_id": principal.user_id})
    if blocked is None:
        raise HTTPException(404, "Account not found.")
    if blocked:
        raise HTTPException(403, "Your reporting privileges have been blocked by an administrator.")
    if request.target_user_id == principal.user_id:
        raise HTTPException(409, "You cannot report yourself or your own work.")
    target_exists = await session.scalar(text("select exists(select 1 from user_accounts where user_id=:user_id and account_status='active' and email_verified_at is not null)"), {"user_id": request.target_user_id})
    if not target_exists:
        raise HTTPException(404, "The reported account is unavailable.")
    if request.target_type == "work":
        work_exists = await session.scalar(text("select exists(select 1 from works where work_id=:work_id and owner_user_id=:owner_id and status='published')"), {"work_id": request.target_work_id, "owner_id": request.target_user_id})
        if not work_exists:
            raise HTTPException(404, "The reported work is unavailable.")
    try:
        await session.execute(text("insert into content_reports(reporter_user_id,target_type,target_user_id,target_work_id,reason_code,details) values(:reporter,:target_type,:target_user,:target_work,:reason,:details)"), {"reporter": principal.user_id, "target_type": request.target_type, "target_user": request.target_user_id, "target_work": request.target_work_id, "reason": request.reason_code, "details": request.details})
        await session.commit()
        await notify_report_managers(session)
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(409, "You have already reported this subject.") from error
    return Response(status_code=204)


@router.get("", response_model=ReportPage)
async def list_reports(_: Annotated[Principal, Depends(require_permission("reports.manage"))], session: Annotated[AsyncSession, Depends(get_database_session)], status: str | None = Query(default=None, pattern="^(pending|reviewed|dismissed|actioned)$"), limit: int = Query(25, ge=1, le=100), cursor: int = Query(0, ge=0, le=100_000)) -> ReportPage:
    rows = (await session.execute(text("""
        select r.*, coalesce(reporter.full_name,'Unknown account') reporter_name,
               coalesce(reporter_account.reporting_blocked,false) reporter_reporting_blocked,
               coalesce(reporter_account.user_id is not null and reporter_role.role_code in ('user','supervisor'),false) reporter_can_be_restricted,
               coalesce(target.full_name,'Removed account') target_user_name, w.title target_work_title
        from content_reports r
        left join user_profiles reporter on reporter.user_id=r.reporter_user_id
        left join user_accounts reporter_account on reporter_account.user_id=r.reporter_user_id
        left join user_roles reporter_role on reporter_role.user_id=r.reporter_user_id
        left join user_profiles target on target.user_id=r.target_user_id
        left join works w on w.work_id=r.target_work_id
        where (cast(:status as text) is null or r.status=cast(:status as text))
        order by r.created_at desc, r.report_id desc limit :limit offset :cursor
    """), {"status": status, "limit": limit + 1, "cursor": cursor})).mappings().all()
    return ReportPage(items=[ReportItem(**row) for row in rows[:limit]], next_cursor=cursor + limit if len(rows) > limit else None)


@router.patch("/{report_id}", status_code=204)
async def review_report(report_id: UUID, request: ReviewReportRequest, principal: Annotated[Principal, Depends(require_permission("reports.manage"))], session: Annotated[AsyncSession, Depends(get_database_session)]) -> Response:
    notes = " ".join(request.notes.split()) if request.notes else None
    result = await session.execute(text("update content_reports set status=:status,reviewer_user_id=:reviewer,reviewer_notes=:notes,reviewed_at=now() where report_id=:report_id returning report_id"), {"status": request.status, "reviewer": principal.user_id, "notes": notes, "report_id": report_id})
    if result.scalar_one_or_none() is None:
        raise HTTPException(404, "Report not found.")
    await session.commit()
    await notify_report_managers(session)
    return Response(status_code=204)
