from types import TracebackType
from typing import Any

import httpx
import pytest

from src.infrastructure.integrations.brevo_email import BrevoVerificationEmailGateway


class FakeAsyncClient:
    payloads: list[dict[str, Any]] = []

    def __init__(self, *, timeout: float) -> None:
        assert timeout == 10.0

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    async def post(self, url: str, **kwargs: Any) -> httpx.Response:
        assert url == "https://api.brevo.com/v3/smtp/email"
        self.payloads.append(kwargs["json"])
        return httpx.Response(201)


@pytest.mark.asyncio
async def test_verification_and_reset_use_the_same_brevo_template(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    FakeAsyncClient.payloads = []
    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    gateway = BrevoVerificationEmailGateway(
        "api-key", "no-reply@mail.inkfig-hu.com", "InkFig", 123
    )

    await gateway.send_verification_code(
        "12345678@students.hebron.edu", "Student", "123456", 10
    )
    await gateway.send_password_reset_code(
        "12345678@students.hebron.edu", "Student", "654321", 10
    )

    verification, reset = FakeAsyncClient.payloads
    assert verification["templateId"] == reset["templateId"] == 123
    assert verification["params"]["code_purpose"] == "complete your InkFig registration"
    assert reset["params"]["code_purpose"] == "reset your InkFig password"
    assert reset["subject"] == "Your InkFig password reset code"
    assert "htmlContent" not in reset
