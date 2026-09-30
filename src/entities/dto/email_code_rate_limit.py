from pydantic import BaseModel, Field


class EmailCodeRateDecision(BaseModel):
    allowed: bool
    retry_after_seconds: int = Field(ge=0)
    hourly_limit_reached: bool = False
