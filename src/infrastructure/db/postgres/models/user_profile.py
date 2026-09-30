from datetime import date, datetime
from uuid import UUID

from sqlalchemy import Boolean, Date, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.db.postgres.base import Base


class UserProfileModel(Base):
    __tablename__ = "user_profiles"

    user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(16), nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    email_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )


class EmailVerificationCodeModel(Base):
    __tablename__ = "email_verification_codes"

    verification_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), nullable=False)
    code_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    invalidated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sent_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
