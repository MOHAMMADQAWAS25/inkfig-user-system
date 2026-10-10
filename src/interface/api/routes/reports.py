from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from pydantic import BaseModel, Field, model_validator
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.postgres.session import get_database_session
from src.interface.dependencies.authorization import Principal, require_permission

router = APIRouter(prefix="/reports", tags=["reports"])
ReasonCode = Literal["harassment", "hate_speech", "sexual_content", "violence", "spam", "copyright", "impersonation", "other"]
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
        if self.details is not None:
            self.details = " ".join(self.details.split()) or None
            if self.details is not None and len(self.details) < 10:
                raise ValueError("Report details must contain at least 10 characters.")
        return self


class ReviewReportRequest(BaseModel):
    status: Literal["reviewed", "dismissed", "actioned"]
    notes: str | None = Field(default=None, max_length=2000)


class ReportItem(BaseModel):
    report_id: UUID
    reporter_user_id: UUID
    reporter_name: str
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


@router.post("", status_code=204)
async def create_report(request: CreateReportRequest, principal: Annotated[Principal, Depends(require_permission("reports.create"))], session: Annotated[AsyncSession, Depends(get_database_session)]) -> Response:
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
    except IntegrityError as error:
        await session.rollback()
        raise HTTPException(409, "You have already reported this subject.") from error
    return Response(status_code=204)


@router.get("", response_model=ReportPage)
async def list_reports(_: Annotated[Principal, Depends(require_permission("reports.manage"))], session: Annotated[AsyncSession, Depends(get_database_session)], status: str | None = Query(default=None, pattern="^(pending|reviewed|dismissed|actioned)$"), limit: int = Query(25, ge=1, le=100), cursor: int = Query(0, ge=0, le=100_000)) -> ReportPage:
    rows = (await session.execute(text("""
        select r.*, coalesce(reporter.full_name,'Unknown account') reporter_name,
               coalesce(target.full_name,'Removed account') target_user_name, w.title target_work_title
        from content_reports r
        left join user_profiles reporter on reporter.user_id=r.reporter_user_id
        left join user_profiles target on target.user_id=r.target_user_id
        left join works w on w.work_id=r.target_work_id
        where (:status is null or r.status=:status)
        order by r.created_at desc, r.report_id desc limit :limit offset :cursor
    """), {"status": status, "limit": limit + 1, "cursor": cursor})).mappings().all()
    return ReportPage(items=[ReportItem(**row) for row in rows[:limit]], next_cursor=cursor + limit if len(rows) > limit else None)


@router.patch("/{report_id}", status_code=204)
async def review_report(report_id: UUID, request: ReviewReportRequest, principal: Annotated[Principal, Depends(require_permission("reports.manage"))], session: Annotated[AsyncSession, Depends(get_database_session)]) -> Response:
    notes = " ".join(request.notes.split()) if request.notes else None
    result = await session.execute(text("update content_reports set status=:status,reviewer_user_id=:reviewer,reviewer_notes=:notes,reviewed_at=now() where report_id=:report_id"), {"status": request.status, "reviewer": principal.user_id, "notes": notes, "report_id": report_id})
    if result.rowcount == 0:
        raise HTTPException(404, "Report not found.")
    await session.commit()
    return Response(status_code=204)
