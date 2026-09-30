from html import escape

import httpx

from src.entities.exceptions.registration import EmailDeliveryError


class BrevoVerificationEmailGateway:
    def __init__(
        self,
        api_key: str,
        sender_email: str,
        sender_name: str,
        template_id: int,
    ) -> None:
        if not api_key or not sender_email or not sender_name or template_id <= 0:
            raise RuntimeError("Brevo email configuration is required.")
        self._api_key = api_key
        self._sender_email = sender_email
        self._sender_name = sender_name
        self._template_id = template_id

    async def send_verification_code(
        self, email: str, full_name: str, code: str, expires_minutes: int
    ) -> None:
        payload = {
            "sender": {"email": self._sender_email, "name": self._sender_name},
            "to": [{"email": email, "name": full_name}],
            "templateId": self._template_id,
            "params": {
                "full_name": full_name,
                "verification_code": code,
                "expires_minutes": expires_minutes,
            },
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={"api-key": self._api_key, "Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.RequestError as error:
            raise EmailDeliveryError("Brevo was unreachable.") from error
        if response.status_code not in {200, 201, 202}:
            raise EmailDeliveryError(
                f"Brevo rejected the verification email with status {response.status_code}."
            )

    async def send_password_reset_code(
        self, email: str, full_name: str, code: str, expires_minutes: int
    ) -> None:
        safe_name = escape(full_name)
        payload = {
            "sender": {"email": self._sender_email, "name": self._sender_name},
            "to": [{"email": email, "name": full_name}],
            "subject": "Your InkFig password reset code",
            "htmlContent": (
                f"<p>Hello {safe_name},</p>"
                "<p>Use this code to reset your InkFig password:</p>"
                f"<p style='font-size:28px;font-weight:700;letter-spacing:6px'>{code}</p>"
                f"<p>This code expires in {expires_minutes} minutes.</p>"
                "<p>If you did not request this reset, you can ignore this email.</p>"
            ),
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    "https://api.brevo.com/v3/smtp/email",
                    headers={"api-key": self._api_key, "Content-Type": "application/json"},
                    json=payload,
                )
        except httpx.RequestError as error:
            raise EmailDeliveryError("Brevo was unreachable.") from error
        if response.status_code not in {200, 201, 202}:
            raise EmailDeliveryError(
                f"Brevo rejected the reset email with status {response.status_code}."
            )
