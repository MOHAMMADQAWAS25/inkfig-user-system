from datetime import datetime, timedelta
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entities.dto.email_code_rate_limit import EmailCodeRateDecision
from src.infrastructure.db.postgres.models.user_profile import EmailCodeRateLimitModel


class SqlAlchemyEmailCodeRateLimitRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def reserve_send(
        self,
        scope: str,
        identifier_hash: str,
        now: datetime,
        cooldown_seconds: int,
        max_sends: int,
        block_seconds: int,
    ) -> EmailCodeRateDecision:
        lock_key = f"{scope}:{identifier_hash}"
        await self._session.execute(
            select(func.pg_advisory_xact_lock(func.hashtextextended(lock_key, 0)))
        )
        record = await self._session.get(
            EmailCodeRateLimitModel,
            {"scope": scope, "identifier_hash": identifier_hash},
        )
        if record is None:
            record = EmailCodeRateLimitModel(
                scope=scope,
                identifier_hash=identifier_hash,
                send_count=0,
            )
            self._session.add(record)

        if record.blocked_until is not None and record.blocked_until > now:
            retry_after = ceil((record.blocked_until - now).total_seconds())
            await self._session.commit()
            return EmailCodeRateDecision(
                allowed=False,
                retry_after_seconds=retry_after,
                hourly_limit_reached=True,
            )

        if record.blocked_until is not None:
            record.send_count = 0
            record.blocked_until = None
            record.last_sent_at = None

        if record.last_sent_at is not None:
            cooldown_until = record.last_sent_at + timedelta(seconds=cooldown_seconds)
            if cooldown_until > now:
                retry_after = ceil((cooldown_until - now).total_seconds())
                await self._session.commit()
                return EmailCodeRateDecision(
                    allowed=False,
                    retry_after_seconds=retry_after,
                )

        record.send_count += 1
        record.last_sent_at = now
        hourly_limit_reached = record.send_count >= max_sends
        retry_after = cooldown_seconds
        if hourly_limit_reached:
            record.blocked_until = now + timedelta(seconds=block_seconds)
            retry_after = block_seconds
        await self._session.commit()
        return EmailCodeRateDecision(
            allowed=True,
            retry_after_seconds=retry_after,
            hourly_limit_reached=hourly_limit_reached,
        )
