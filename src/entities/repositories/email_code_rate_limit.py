from datetime import datetime
from typing import Protocol

from src.entities.dto.email_code_rate_limit import EmailCodeRateDecision


class EmailCodeRateLimitRepository(Protocol):
    async def reserve_send(
        self,
        scope: str,
        identifier_hash: str,
        now: datetime,
        cooldown_seconds: int,
        max_sends: int,
        block_seconds: int,
    ) -> EmailCodeRateDecision: ...
